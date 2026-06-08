import subprocess


def handler(event, context):
    return subprocess.check_output(["whoami"]).decode()
