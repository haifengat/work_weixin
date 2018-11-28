# 企业微信接口

### 项目介绍
封装企业微信接口,发送消息.


### 安装教程

` pip install work_weixin `

### 使用说明

#### config.yml
```yaml
---
# 部门ID
agentid: 10222222
# 钥匙
secret: Zjxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 企业id
corpid: wxxxxxxxxxxxxxxxx
```

#### main.py

```python

from work_weixin import Client
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

    # rtn = client.upload_tmp(r'C:\Users\haifeng\tmp.jpg')
    # rtn = client.send_img(toparty=partid, media_id=rtn['media_id'])
    print(print(rtn['errmsg']))

```