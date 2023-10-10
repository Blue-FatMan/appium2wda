#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time    : 2022/12/9 16:01
# @Author  : 
# @Email   : LQ65535@163.com
# @File    : demo.py
# @desc    : demo
# @Software: PyCharm

import base64
import yaml
import time
from munch import DefaultMunch
import os
import sys

# 添加父目录到系统中，使得可以导入appium2wda
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appium2wda import webdriver
# TouchAction = webdriver.TouchAction
# MultiAction = webdriver.MultiAction


def Dict(dict_source):
    """字典转对象（dict -＞ object使key键可以可以用点属性来调用）,例如x.key"""
    return DefaultMunch.fromDict(dict_source)


def get_env_json():
    """
    获取环境json信息
    :return: 返回环境信息json信息
    """
    # 加载手机环境配置信息
    config_path = "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        return Dict(data)


def init_device():
    """
    IOS手机在windows上driver启动方式demo
    :return:
    """
    data = get_env_json()
    data.default = data.iphoneOnWindowsConfig
    desired_caps = data.default
    # 更新其他配置信息
    desired_caps.update(data.defaultApp)

    webDriverAgentUrl = "%s:%s" % (desired_caps.ip, desired_caps.wdaLocalPort)
    desired_caps.update({"webDriverAgentUrl": webDriverAgentUrl})

    driver = webdriver.Remote(desired_caps)
    driver.implicitly_wait(3)

    driver.start_recording_screen(videoType='mpeg4', timeLimit=600)
    time.sleep(10)
    payload = driver.stop_recording_screen()
    with open("test-record.mp4", "wb") as fd:
        fd.write(base64.b64decode(payload))
    print("启动成功")

    return driver


if __name__ == '__main__':
    init_device()
