import paramiko
import requests
from celery import shared_task
from studentmgr.models import Submission


@shared_task(time_limit=300)
def do_container_eval_cc(*args, **kwargs):
    sub = Submission.objects.get(id=kwargs.get('sub_id'))
    ip = sub.public_ip_address
    username = sub.username
    path_to_key = sub.private_key_file.path

    marks = 0
    message = ""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username=username, key_filename=path_to_key)
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.Image}}'")
        output = stdout.read().decode()
        if "users:latest" in output:
            message += "Users container running. "
            marks += 0.5
        else:
            message += "Users container not running. "
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.Image}}'")
        output = stdout.read().decode()
        if "rides:latest" in output:
            message += "Rides container running. "
            marks += 0.5
        else:
            message += "Rides container not running. "
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.ID}} {{.Image}}  {{.Names}}' | grep users:latest | cut -d ' ' -f 3")
        con_id = str(stdout.read().decode())
        stdin, stdout, stderr = ssh.exec_command("sudo docker exec "+con_id+" env printenv TEAM_NAME")
        team_name = str(stdout.read().decode())
        print("CONID", con_id)
        con_id = con_id.strip()
        print("CONID", con_id)
        print("sudo docker exec "+con_id+" env printenv TEAM_NAME")
        print("TEAMNAME", team_name)
        if sub.team.team_name in team_name:
            message += "Team name set in users container. "
            marks += 0.5
        else:
            message += "Team name not set in users container. "
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.ID}} {{.Image}} {{.Names}}' | grep rides:latest | cut -d ' ' -f 3")
        con_id = str(stdout.read().decode())
        stdin, stdout, stderr = ssh.exec_command("sudo docker exec " + con_id + " env printenv TEAM_NAME")
        team_name = str(stdout.read().decode())
        print("CONID", con_id)
        con_id = con_id.strip()
        print("CONID", con_id)
        print("sudo docker exec " + con_id + " env printenv TEAM_NAME")
        print("TEAMNAME", team_name)
        if sub.team.team_name in team_name:
            message += "Team name set in rides container. "
            marks += 0.5
        else:
            message += "Team name not set in rides container. "

        r = requests.post("http://"+sub.public_ip_address+":8080/api/v1/db/clear")
        if r.status_code == 200:
            marks += 0.5
            message += "Clear db API success on users microservice. "
        else:
            message += "Clear db API failure on users microservice. "

        r = requests.post("http://" + sub.public_ip_address + ":8000/api/v1/db/clear")
        if r.status_code == 200:
            marks += 0.5
            message += "Clear db API success on rides microservice. "
        else:
            message += "Clear db API failure on rides microservice. "

        r = requests.put("http://" + sub.public_ip_address + ':8080/api/v1/users',
                         json={'username': 'userName', 'password': '3d725109c7e7c0bfb9d709836735b56d943d263f'})
        if r.status_code == 201:
            marks += 0.5
            message += "Passed Add user. "
        else:
            message += "Failed add user. "

        r = requests.get("http://" + sub.public_ip_address + ":8080/api/v1/users")
        if r.status_code == 200:
            marks += 0.5
            message += "List all users API success on users microservice. "
        else:
            message += "List all users API failure on users microservice. "
        sub.marks = marks
        sub.message = message
        sub.save()

    except Exception as e:
        print("ERROR: ", e)
        marks += 0
        message += "Fatal Error.! Check if your instance is running/ pem file is correct etc"
        sub.message = message
        sub.marks = marks
        sub.save()


