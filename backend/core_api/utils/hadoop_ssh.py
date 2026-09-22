import paramiko
from django.conf import settings
import os

class HadoopTaskRunner:
    def __init__(self):
        self.hostname = '192.168.x.x' 
        self.port = 22
        self.username = 'hadoop' 
        self.key_path = os.path.join(settings.BASE_DIR, 'ssh_keys', 'id_rsa') 

    def _get_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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

    def run_sqoop_import(self):
        command = """
        sqoop import \
        --connect jdbc:mysql://<WINDOWS_IP>:3306/bigdata_db \
        --username root \
        --password <mat_khau_mysql> \
        --table raw_data_table \
        --target-dir /user/hadoop/project/input_data \
        -m 1
        """
        return self.execute_command(command)

    def run_mapreduce_job(self, input_dir="/user/hadoop/project/input_data", output_dir="/user/hadoop/project/mr_output"):
        jar_path = "/home/hadoop/jobs/bigdata_mapreduce.jar"
        main_class = "com.project.bigdata.MainDriver"
        clear_output_cmd = f"hdfs dfs -rm -r -skipTrash {output_dir}"
        self.execute_command(clear_output_cmd)
        run_mr_cmd = f"hadoop jar {jar_path} {main_class} {input_dir} {output_dir}"
        return self.execute_command(run_mr_cmd)
