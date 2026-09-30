import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.RSAKey.from_private_key_file("c:\\Users\\Laptop\\Documents\\GitHub\\bigdata_project\\backend\\ssh_keys\\id_rsa")
client.connect(hostname="192.168.10.10", username="hadoopthuc", pkey=key)

print("Killing stuck Pig process...")
stdin, stdout, stderr = client.exec_command("kill -9 36636")
print(stdout.read().decode())
client.close()
