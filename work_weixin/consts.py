#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : HaiFeng
# @Email   : 24918700@qq.com
# @Time    : 2018/11/24
# @desc    : 定义常量

API_URL = 'https://qyapi.weixin.qq.com'
GET_ACCESS_TOKEN = '/cgi-bin/gettoken'
GET_DEPARTMENT = '/cgi-bin/department/list'
GET_USER_LIST = '/cgi-bin/user/simplelist'
SEND_MSG = '/cgi-bin/message/send'
UPLOAD_TMP = '/cgi-bin/media/upload'
UPLOAD_IMG = '/cgi-bin/media/uploadimg'
CREATE_MENU = '/cgi-bin/menu/create'
DELETE_MENU = '/cgi-bin/menu/delete'

CONTENT_TYPE = 'Content-Type'
CONTENT_LENGTH = 'Content-Length'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-agent_id'

ACEEPT = 'Accept'
COOKIE = 'Cookie'
LOCALE = 'Locale='

APPLICATION_JSON = 'application/json'

GET = "GET"
POST = "POST"