#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time    : 2021/10/13 14:40
# @Author  : 
# @Email   : LQ65535@163.com
# @File    : webdriver.py
# @Software: PyCharm
import json

import time
import sys
import os
import selenium.common.exceptions as selenium_error
import copy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加 local-packages 目录
sys.path.insert(0, os.path.join(BASE_DIR, '../', '../', 'localPackages'))
from appium2wda import wda
wda.DEBUG = False

from appium2wda.webdriver_ios import element_transform
from appium2wda.webdriver_ios._tidevice_relay import TideviceRelay
from appium2wda.webdriver_ios.recordscreen import ScreenRecord


class Webdriver(object):

    def __init__(self, *args, **kwargs):
        """
        driver初始化
        调用方式一：类类似于appium的方式，有两个参数 webdriver('http://127.0.0.1:4725/wd/hub', desired_capabilities)
        调用方式二：直接调用facebook-wda的方式， webdriver(desired_capabilities)
        :param args:
        :param kwargs:
        """
        self.params = args
        self.desired_capabilities = dict()
        self.wda_bundle_id = None
        if len(self.params) == 2:
            # self.request_url = args[0]
            self.desired_caps = args[1]
        elif len(self.params) == 1:
            self.desired_caps = args[0]
        elif kwargs.get("desired_capabilities", None):
            self.desired_caps = kwargs.get("desired_capabilities")

        self.device_id = self.desired_caps["udid"]
        self.port = self.desired_caps["wdaLocalPort"]
        self.bundle_id = self.desired_caps["bundleId"]
        self.mjpegServerPort = self.desired_caps.get("mjpegServerPort", None)

        self.desired_capabilities["desired"] = self.desired_caps
        self.desired_capabilities.update(self.desired_caps)

        # adapt appium different version
        self.capabilities = copy.deepcopy(self.desired_capabilities)

        if self.desired_caps.get("wda_bundle_id", None):
            self.wda_bundle_id = self.desired_caps.get("wda_bundle_id")
        self.driver = self.client()

    def client(self):
        """启动一个session"""
        __client = wda.USBClient(self.device_id, port=self.port, wda_bundle_id=self.wda_bundle_id, mjpeg_server_port=self.mjpegServerPort)
        session = __client.session(self.bundle_id)
        return session

    @property
    def http(self):
        """返回driver的http对象"""
        res = self.driver.http
        return res

    @property
    def session_id(self):
        """ 返回session id"""
        return self.driver.session_id

    def __find_element(self, find_element_str):
        """查找元素，内部调用"""
        if isinstance(find_element_str, dict):
            return self.driver(**find_element_str)
        return self.driver(find_element_str)

    def __find_elements(self, find_element_str):
        """查找元素，内部调用"""
        if isinstance(find_element_str, dict):
            return self.driver(**find_element_str).find_elements()
        return self.driver(find_element_str).find_elements()

    def get_screenshot_as_file(self, filename, *args, **kwargs):
        """截图，并且保存为一个文件"""
        self.driver.screenshot(filename, *args, **kwargs)

    def implicitly_wait(self, seconds):
        self.driver.implicitly_wait(seconds)

    def find_element(self, *args, **kwargs):
        """查找元素，供外部调用"""
        if isinstance(args, tuple):
            by, element_tag = args
            by, element_tag = by.strip(), element_tag
        else:
            raise ValueError("params error")
        process = getattr(element_transform, element_transform.SelectorMap.get(by))
        find_element_str = process(element_tag)
        result = self.__find_element(find_element_str)
        try:
            # 这里需要判断一下元素是否存在，如果不存在，则报出NoSuchElement的异常
            element_exists = result.exists
            if not element_exists:
                raise selenium_error.NoSuchElementException("NoSuchElement:({} {})".format(by, element_tag))
        except Exception as e:
            raise selenium_error.NoSuchElementException("NoSuchElement:({} {})".format(by, element_tag))

        return result

    def find_elements(self, *args, **kwargs):
        """查找元素，供外部调用"""
        if isinstance(args, tuple):
            by, element_tag = args
            by, element_tag = by.strip(), element_tag
        else:
            raise ValueError("params error")
        process = getattr(element_transform, element_transform.SelectorMap.get(by))
        find_element_str = process(element_tag)
        result = self.__find_elements(find_element_str)
        try:
            # 这里需要判断一下元素是否存在，如果不存在，则报出NoSuchElement的异常
            if isinstance(result, list):
                pass
            else:
                element_exists = result.exists
                if not element_exists:
                    raise selenium_error.NoSuchElementException("NoSuchElement:({} {})".format(by, element_tag))
        except Exception as e:
            raise selenium_error.NoSuchElementException("NoSuchElement:({} {})".format(by, element_tag))
        return result

    def tap(self, *args, **kwargs):
        """点击像素动作
        使用方式：driver.tap(100, 100) 或者 driver.tap(x=100, y=100)，也可以driver.tap((100, 100))
        """
        params = args[0]
        if isinstance(params, list):
            for item in params:
                self.driver.tap(*item, **kwargs)
        elif isinstance(params, tuple):
            for item in params:
                self.driver.tap(*item, **kwargs)
        else:
            self.driver.tap(*args, **kwargs)

    def drag_and_drop(self, start_ele, end_ele, *args, **kwargs):
        """
        拖动元素到指定位置
        :param start_ele: 要拖动的元素
        :param end_ele: 要拖动到此元素位置
        :return:
        """
        x1, y1 = start_ele.bounds[:2]
        x2, y2 = end_ele.bounds[:2]
        self.driver.swipe(x1, y1, x2, y2, *args, **kwargs)

    def source(self, *args, **kwargs):
        """返回页面原始资源"""
        return self.driver.source(*args, **kwargs)

    def page_source(self, *args, **kwargs):
        """返回页面原始资源"""
        return self.source(*args, **kwargs)

    def get_window_size(self):
        """ 获取手机的屏幕大小"""
        window_size_obj = self.driver.window_size()
        window_size = {
            "width": window_size_obj.width,
            "height": window_size_obj.height,
        }
        return window_size

    def get_mobile_status(self):
        """ 获取手机状态"""
        return self.http.get('/status')

    def start_recording_screen(self, **options):
        """ 开始录制屏幕
        首先，在WDA启动参数中添加MJPEG_SERVER_PORT = 9100，当然端口可以随意指定,
        然后使用iproxy转发一下端口，接着用浏览器打开localhost:9100,图像就出来了。
        https://blog.51cto.com/u_15649298/5719641
        """
        self.tidevice_replay = TideviceRelay(self.device_id, self.mjpegServerPort, self.mjpegServerPort)
        self.tidevice_replay.start()
        self.record_obj = ScreenRecord()
        return self.record_obj.start_recording_screen(mjpegServerPort=self.mjpegServerPort, **options)

        # wda.logger.error("WDA not support recording screen currently!!!")
        # RuntimeError("WDA not support recording screen currently!!!")

    def stop_recording_screen(self, **options):
        """ 结束录制屏幕"""
        self.tidevice_replay.stop()
        return self.record_obj.stop_recording_screen(**options)

        # wda.logger.error("WDA not support recording screen currently!!!")
        # RuntimeError("WDA not support recording screen currently!!!")

    def launch_app(self, *args, **kwargs):
        self.driver.app_launch(*args, **kwargs)

    def activate_app(self, *args, **kwargs):
        self.driver.app_activate(*args, **kwargs)

    def terminate_app(self, *args, **kwargs):
        # Deprecated, use app_stop instead
        return self.driver.app_terminate(*args, **kwargs)

    def start_app(self, *args, **kwargs):
        return self.driver.app_start(*args, **kwargs)

    def stop_app(self, *args, **kwargs):
        return self.driver.app_stop(*args, **kwargs)

    def quit(self):
        """关闭session
        :return:
        """
        self.driver.close()


class TouchAction(object):
    def __init__(self, driver=None):
        self.driver = driver
        self._driver = driver
        self._actions = []

    def tap(self, element=None, x=None, y=None, count=1):
        """Perform a tap action on the element

        Args:
            element (`WebElement`): the element to tap
            x (:obj:`int`, optional): x coordinate to tap, relative to the top left corner of the element.
            y (:obj:`int`, optional): y coordinate. If y is used, x must also be set, and vice versa

        Returns:
            `TouchAction`: self instance
        """
        opts = self._get_opts(element, x, y)
        opts['count'] = count
        self._add_action('tap', opts)

        return self

    def press(self, el=None, x=None, y=None, pressure=None):
        """Begin a chain with a press down action at a particular element or point

        Args:
            el (:obj:`WebElement`, optional): the element to press
            x (:obj:`int`, optional): x coordiate to press. If y is used, x must also be set
            y (:obj:`int`, optional): y coordiate to press. If x is used, y must also be set
            pressure (:obj:`float`, optional): [iOS Only] press as force touch. Read the description of `force` property on Apple's UITouch class
                                (https://developer.apple.com/documentation/uikit/uitouch?language=objc) for more details on possible value ranges.

        Returns:
            `TouchAction`: self instance
        """
        self._add_action('press', self._get_opts(el, x, y, pressure=pressure))

        return self

    def long_press(self, el=None, x=None, y=None, duration=1000):
        """Begin a chain with a press down that lasts `duration` milliseconds

        Args:
            el (:obj:`WebElement`, optional): the element to press
            x (:obj:`int`, optional): x coordiate to press. If y is used, x must also be set
            y (:obj:`int`, optional): y coordiate to press. If x is used, y must also be set
            duration (:obj:`int`, optional): Duration to press

        Returns:
            `TouchAction`: self instance
        """
        self._add_action('longPress', self._get_opts(el, x, y, duration))

        return self

    def wait(self, ms=0):
        """Pause for `ms` milliseconds.

        Args:
            ms (int): The time to pause

        Returns:
            `TouchAction`: self instance
        """
        if ms is None:
            ms = 0

        opts = {'ms': ms}

        self._add_action('wait', opts)

        return self

    def move_to(self, el=None, x=None, y=None):
        """Move the pointer from the previous point to the element or point specified

        Args:
            el (:obj:`WebElement`, optional): the element to be moved to
            x (:obj:`int`, optional): x coordiate to be moved to. If y is used, x must also be set
            y (:obj:`int`, optional): y coordiate to be moved to. If x is used, y must also be set

        Returns:
            `TouchAction`: self instance
        """
        self._add_action('moveTo', self._get_opts(el, x, y))

        return self

    def release(self):
        """End the action by lifting the pointer off the screen

        Returns:
            `TouchAction`: self instance
        """
        self._add_action('release', {})

        return self

    def perform(self):
        """Perform the action by sending the commands to the server to be operated upon

        Returns:
            `TouchAction`: self instance
        """
        params = {'actions': self._actions}
        self._driver.http.post('/session/%s/wda/touch/perform' % self._driver.session_id, data=params)

        # for action in self._actions:
        #     count = action.get("options").get("count")
        #     for _ in range(count):
        #         del action["options"]["count"]
        #         if action["action"] == "tap":
        #             self._driver.tap(**action["options"])

        # get rid of actions so the object can be reused
        self._actions = []

        return self

    @property
    def json_wire_gestures(self):
        gestures = []
        for action in self._actions:
            gestures.append(copy.deepcopy(action))
        return gestures

    def _add_action(self, action, options):
        gesture = {
            'action': action,
            'options': options,
        }
        self._actions.append(gesture)

    def _get_opts(self, element, x, y, duration=None, pressure=None):
        opts = {}
        if element is not None:
            opts['element'] = element.id

        # it makes no sense to have x but no y, or vice versa.
        if x is not None and y is not None:
            opts['x'] = x
            opts['y'] = y

        if duration is not None:
            opts['duration'] = duration

        if pressure is not None:
            opts['pressure'] = pressure

        return opts


class MultiAction(object):
    def __init__(self, driver, element=None):
        self._driver = driver
        self._element = element
        self._touch_actions = []

    def add(self, *touch_actions):
        """Add TouchAction objects to the MultiAction, to be performed later.

        Args:
            touch_actions (`TouchAction`): one or more TouchAction objects describing a chain of actions to be performed by one finger

        Usage:
            a1 = TouchAction(driver)
            a1.press(el1).move_to(el2).release()
            a2 = TouchAction(driver)
            a2.press(el2).move_to(el1).release()

            MultiAction(driver).add(a1, a2)
        """
        for touch_action in touch_actions:
            if self._touch_actions is None:
                self._touch_actions = []

            self._touch_actions.append(copy.copy(touch_action))

    def perform(self):
        """Perform the actions stored in the object.

        Usage:
            a1 = TouchAction(driver)
            a1.press(el1).move_to(el2).release()
            a2 = TouchAction(driver)
            a2.press(el2).move_to(el1).release()

            MultiAction(driver).add(a1, a2).perform()
        """
        params = self.json_wire_gestures
        self._driver.http.post('/session/%s/wda/touch/multi/perform' % self._driver.session_id, data=params)

        # clean up and be ready for the next batch
        self._touch_actions = []

        return self

    @property
    def json_wire_gestures(self):
        actions = []
        for action in self._touch_actions:
            actions.append(action.json_wire_gestures)
        if self._element is not None:
            return {'actions': actions, 'elementId': self._element.id}
        return {'actions': actions}


if __name__ == '__main__':
    pass
