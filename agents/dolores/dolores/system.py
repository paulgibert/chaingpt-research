# stdlib
from typing import Tuple, Dict
import subprocess
import os
import uuid
import shutil

# 3rd party
from sh import docker


def _random_container_name() -> str:
    return "dolores-" + str(uuid.uuid4())[-8:]


def _random_log_id() -> str:
    return "log-" + str(uuid.uuid4())[-8:]


class MissingSystemEnvError(Exception):
    pass


class SystemEnvironment:
    def __init__(self, url: str, branch_or_tag: str=None, dockerfile_path: str="."):
        self.url = url
        self.branch_or_tag = branch_or_tag
        self._curr_container = None
        docker.build("-t", "dolores-image", dockerfile_path)

        self.path = "/tmp/dolores"
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.logs_dir = os.path.join(self.path, "logs")
        if os.path.exists(self.logs_dir):
            shutil.rmtree(self.logs_dir)
        os.mkdir(self.logs_dir)

    def init_env(self) -> str:
        if self._curr_container is not None:
            docker.stop(self._curr_container)
            docker.container("rm", self._curr_container)

        self._curr_container = _random_container_name()
        docker.run("-d", "--name", self._curr_container, "dolores-image", "watch", "date >> /var/log/date.log")

        cmd = f"git clone {self.url} repo"
        if self.branch_or_tag is not None:
            cmd += " -b " + self.branch_or_tag

        subprocess.run(f"docker exec {self._curr_container} sh -c \"{cmd}\"", shell=True, check=False)
        return self._curr_container

    def _exec(self, command: str) -> Tuple[str, str, str]:
        stdout_text = ""
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True)
        while True:
            stdout_line = process.stdout.readline()
            if (not stdout_line) and (process.poll() is not None):
                break
            if stdout_line:
                print(stdout_line.decode('utf-8'), end='')
                stdout_text += stdout_line.decode('utf-8')

        stderr_text = process.stderr.read().decode('utf-8')

        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()

        return return_code, stdout_text, stderr_text

    def exec(self, command: str) -> Dict:
        if self._curr_container is None:
            raise MissingSystemEnvError("You must init a system environment before executing commands")

        docker_cmd = f"docker exec -it -w /work/repo {self._curr_container} {command}"

        return_code, stdout, stderr = self._exec(docker_cmd)

        # Save the log file
        log_id = _random_log_id()
        log_path = os.path.join(self.logs_dir, log_id)
        if os.path.exists(log_path):
            os.remove(log_path)

        with open(log_path, "w", encoding="utf-8") as f:
            f.write("COMMAND: " + command)
            f.write("\n\nRETURN CODE: " + str(return_code))
            f.write("\n\nSTDOUT:\n\n" + stdout)
            f.write("\n\nSTDERR:\n\n" + stderr)

        if len(stdout) > 1000:
            stdout = "[Too long. See log for full output]"

        if len(stderr) > 1000:
            stderr = "[Too long. See log for full output]"

        return {
            "returncode": return_code,
            "stdout": stdout,
            "stderr": stderr,
            "log_id": log_id 
        }

    def read_log(self, log_id: str) -> str:
        # TODO: Consider a bottom up read approach with early stopping
        log_path = os.path.join(self.logs_dir, log_id)
        if not os.path.exists(log_path):
            raise ValueError(f"{log_id} is not a valid log file id")

        with open(log_path, "r", encoding="utf-8") as f:
            text = f.read()
            return text
