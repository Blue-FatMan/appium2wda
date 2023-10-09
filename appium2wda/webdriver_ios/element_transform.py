#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time    : 2021/10/13 17:51
# @Author  : liuqiao
# @Email   : liuqiao@LQ65535@163.com
# @File    : element_transform.py
# @Software: PyCharm

SelectorMap = {
    "-ios predicate string": "ios_predicate_string",
    "-ios class chain": "ios_class_chain",
    "xpath": "xpath_find",
    "name": "name_find",
    "id": "id_find",
    "label": "label_find",
    "class name": "classname_find",
    "value": "value_find"
}


def ios_predicate_string(element):
    """element:'label == "超时未上锁告警设置" AND name == "超时未上锁告警设置" AND value == "超时未上锁告警设置"'
    或者 label == "超时未上锁告警设置"
    """
    # elements = element.split("AND")
    # if len(elements) >= 2:
    #     result = element
    # else:
    #     tag, value = elements[0].split("==")
    #     result = "{}={}".format(tag.strip(), value.strip())
    result = element
    return result


def ios_class_chain(element):
    result = {"classChain": element}
    return result


def xpath_find(element):
    """ element
    :param element:
    :return:
    """
    result = {"xpath": element}
    return result


def name_find(element):
    """ element
    :param element:
    :return:
    """
    result = {"name": element}
    return result


def id_find(element):
    """ element
    :param element:
    :return:
    """
    result = {"id": element}
    return result


def label_find(element):
    """ element
    :param element:
    :return:
    """
    result = {"label": element}
    return result


def classname_find(element):
    """ element
    :param element:
    :return:
    """
    result = {"className": element}
    return result


def value_find(element):
    """ element
    :param element:
    :return:
    """
    result = {"value": element}
    return result
