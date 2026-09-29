import paramiko
from django.conf import settings
import os

class HadoopTaskRunner:
    def __init__(self, hostname=None, port=22, username=None, password=None, key_path=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path or os.path.join(settings.BASE_DIR, 'ssh_keys', 'id_rsa')

    def _get_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.password:
            client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password
            )
        else:
            private_key = paramiko.RSAKey.from_private_key_file(self.key_path)
            client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                pkey=private_key
            )
        return client

    def execute_command(self, command):
        client = None
        try:
            client = self._get_client()
            stdin, stdout, stderr = client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            return {
                "success": exit_status == 0,
                "output": out,
                "error": err
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if client:
                client.close()

    def run_sqoop_import(self, mysql_host, mysql_user, mysql_password, mysql_db, table_name, target_dir):
        command = f"""
        /usr/lib/sqoop/bin/sqoop import \\
        --connect jdbc:mysql://{mysql_host}:3306/{mysql_db} \\
        --username {mysql_user} \\
        --password {mysql_password} \\
        --table {table_name} \\
        --target-dir {target_dir} \\
        --delete-target-dir \\
        --fields-terminated-by '\\t' \\
        -m 1
        """
        return self.execute_command(command)

    def run_mapreduce_job(self, input_dir, output_dir, local_mapper_path, local_reducer_path):
        client = None
        try:
            client = self._get_client()
            # 1. Upload mapper and reducer files using SFTP
            sftp = client.open_sftp()
            sftp.put(local_mapper_path, '/home/hadoopthuc/mapper.py')
            sftp.put(local_reducer_path, '/home/hadoopthuc/reducer.py')
            sftp.close()
            
            # 2. Run Hadoop Streaming command
            command = f"""
            chmod +x /home/hadoopthuc/mapper.py
            chmod +x /home/hadoopthuc/reducer.py
            
            /home/hadoopthuc/hadoop/bin/hdfs dfs -rm -r -skipTrash {output_dir}
            
            STREAMING_JAR="/home/hadoopthuc/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.4.jar"
            
            /home/hadoopthuc/hadoop/bin/hadoop jar $STREAMING_JAR \\
                -files /home/hadoopthuc/mapper.py,/home/hadoopthuc/reducer.py \\
                -mapper "python3 mapper.py" \\
                -reducer "python3 reducer.py" \\
                -input {input_dir} \\
                -output {output_dir}
            """
            
            stdin, stdout, stderr = client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            
            if exit_status == 0:
                # Get the result from HDFS
                read_cmd = f"/home/hadoopthuc/hadoop/bin/hdfs dfs -cat {output_dir}/part-00000"
                _, cat_out, _ = client.exec_command(read_cmd)
                result_data = cat_out.read().decode('utf-8').strip()
                return {"success": True, "output": result_data, "logs": out}
            else:
                return {"success": False, "error": err, "logs": out}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if client:
                client.close()
