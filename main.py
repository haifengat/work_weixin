#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : HaiFeng
# @Email   : 24918700@qq.com
# @Time    : 2018/11/24
# @desc    : 测试接口

from work_api import Client
import getpass
import yaml
import os

if __name__ == '__main__':
    cfg_yml = yaml.load(open('./config.yml', 'r', encoding='utf-8'))
    if 'corpid' in cfg_yml:
        corpid = cfg_yml['corpid']
    else:
        corpid = input('请输入企业ID: ')
    if 'secret' in cfg_yml:
        secret = cfg_yml['secret']
    else:
        secret = getpass.getpass('请输入安全码: ')
    if 'agentid' in cfg_yml:
        agentid = cfg_yml['agentid']
    else:
        agentid = input('请输入组织代码: ')
    client = Client(corpid, secret, agentid)
    print(client.access_token)
    print(client.departments)
    print(client.users)
    partid = list(client.departments.keys())[0]
    msg = f"hello everyone in department of {client.departments[partid]['name']}"
    rtn = client.send_text_toparty(partid, msg)
    print(rtn['errmsg'])

    # rtn = client.upload_tmp(r'C:\Users\haifeng\OneDrive\work_ebfcn\扫码开户.jpg')
    # rtn = client.send_img(toparty=partid, media_id=rtn['media_id'])
    print(print(rtn['errmsg']))

    # rtn = client.create_menu('v001', '金创1号')
    input()
