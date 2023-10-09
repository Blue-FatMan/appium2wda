#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
from appium2wda.webdriver_ios._tidevice_relay import TideviceRelay

if __name__ == '__main__':
    t = TideviceRelay("59290669adf51a4e0", 9100, 9100)
    t.start()
    print(4444)
    time.sleep(20)
    t.stop()
