#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : HaiFeng
# @Email   : 24918700@qq.com
# @Time    : 2018/11/24
# @desc    : 异常类


class WorkException(Exception):

    def __init__(self, response):
        print(response.text + ', ' + str(response.status_code))
        self.code = 0
        try:
            json_res = response.json()
        except ValueError:
            self.message = 'Invalid JSON error message from Okex: {}'.format(response.text)
        else:
            if "errcode" in json_res.keys() and "errmsg" in json_res.keys():
                self.code = json_res['errcode']
                self.message = json_res['errmsg']
            else:
                self.code = 'None'
                self.message = 'Server error'

        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'API Request Error(code={}): {}'.format(self.code, self.message)


class WorkRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'WorkRequestException: {}'.format(self.message)
