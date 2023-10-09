#!/usr/bin/python
# -*- coding: UTF-8 -*-

import shutil
import subprocess
import tempfile
import time
from ._kill_p import kill as pkill

class TideviceRelay(object):
    def __init__(self, udid: str, lport: int, rport: int):
        """
        :param udid: udid
        :param lport: local port
        :param rport: remote port
        """
        self.udid = udid
        self.lport = lport
        self.rport = rport

        # init check
        self.tidevice_execute = None
        self.run_p = None
        self.__check_tidevice()

    def __check_tidevice(self):
        tidevice_execute = shutil.which("tidevice")
        if not tidevice_execute:
            raise RuntimeError(
                "Can not found tidevice.exe in your System environment variables, please use pip install tidevice")
        else:
            self.tidevice_execute = tidevice_execute

    def start(self):
        """
        启动端口转发进程
        """
        cmd = f"{self.tidevice_execute} -u {self.udid} relay {self.lport} {self.rport}"
        # 得到一个临时文件对象， 调用close后，此文件从磁盘删除
        out_temp = tempfile.TemporaryFile(mode='w+')
        # 获取临时文件的文件号
        file_tmp = out_temp.fileno()
        # print(cmd)
        self.run_p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=file_tmp, stderr=file_tmp)

    def stop(self):
        """
        停止进程
        :return:
        """
        # p1.send_signal(signal.CTRL_C_EVENT)
        pkill(self.run_p.pid)


if __name__ == '__main__':
    t = TideviceRelay("59290669adf51a4e06ced4d250b73655c3f5013e", 9102, 9102)
    t.start()
    time.sleep(20)
    t.stop()
