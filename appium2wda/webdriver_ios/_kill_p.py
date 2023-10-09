#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time    : 2023/10/9 11:37
import traceback
import psutil


# http://bcoder.com/others/problem-of-processs-can-not-terminate-in-python-subprocess


def kill(proc_pid):
    """
    Kill along with child processes by pid.
    :param proc_pid:
    :return:
    """

    try:
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except psutil.NoSuchProcess:
        pass
