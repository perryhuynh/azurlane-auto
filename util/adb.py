import subprocess
from util.logger import Logger


class Adb(object):

    @classmethod
    def init(cls):
        """Kills and starts a new ADB server
        """
        cls.kill_server()
        cls.start_server()

    @staticmethod
    def start_server():
        """Starts the ADB server
        """
        cmd = ['adb', 'start-server']
        subprocess.call(cmd)
        cmd = ['adb', 'connect', '127.0.0.1:7555']
        subprocess.call(cmd)

    @staticmethod
    def kill_server():
        """Kills the ADB server
        """
        cmd = ['adb', 'kill-server']
        subprocess.call(cmd)

    @staticmethod
    def exec_out(args):
        """Executes the command via exec-out

        Args:
            args (string): Command to execute.

        Returns:
            tuple: A tuple containing stdoutdata and stderrdata
        """
        cmd = ['adb', 'exec-out'] + args.split(' ')
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        return process.communicate()[0]

    @staticmethod
    def shell(args):
        """Executes the command via adb shell

        Args:
            args (string): Command to execute.
        """
        cmd = ['adb', 'shell'] + args.split(' ')
        subprocess.call(cmd, shell=True)
