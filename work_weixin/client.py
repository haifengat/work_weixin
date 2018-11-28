import requests
from requests_toolbelt import MultipartEncoder
import json
import os
import random
import string

from . import consts as c, utils, exceptions


class Client(object):

    def __init__(self, corpid: str = 'corpid', secret: str = 'secret', agentid='agentid'):
        """
        初始化接口

        :param corpid: 企业ID
        :param secret: 安全码
        :param agentid: 部门ID
        """

        self.agent_id: str = agentid
        self.access_token: str = ''
        # token所有请求均会用到

        result = self._request(c.GET, c.GET_ACCESS_TOKEN, {'corpid': corpid, 'corpsecret': secret})
        if result['errcode'] == 0:
            self.access_token = result['access_token']
        else:
            raise exceptions.WorkException(result)

        self.departments: dict = {}
        '''部门结构'''

        self.users: dict = {}
        '''司员信息'''

        # 取部门
        self._get_departments()
        # 取司员
        for id in self.departments.keys():
            self._get_users(id)

    def _get_departments(self) -> dict:
        """获取组织结构

        Returns
        -------
        result : dict of departments
            {
                "errcode": 0,
                "errmsg": "ok",
                "department": [
                    {
                        "id": 73,
                        "name": "金融创新部",
                        "parentid": 3,
                        "order": 999999987
                    }
                ]
            }

        """
        result = self._request(c.GET, c.GET_DEPARTMENT)
        for part in result['department']:
            self.departments[part['id']] = part

    def _get_users(self, department_id: int = 0):
        """
        获取司员信息

        :param department_id: 部门ID
        :return:
{
   "errcode": 0,
   "errmsg": "ok",
   "userlist": [
           {
                  "userid": "zhangsan",
                  "name": "李四",
                  "department": [1, 2]
           }
     ]
}
        """

        result = self._request(c.GET, c.GET_USER_LIST, {'department_id': department_id})
        for user in result['userlist']:
            self.users[user['userid']] = user

    def send_text_touser(self, touser: str, msg: str):
        """
        发送消息给同事

        :param touser:  "UserID1|UserID2|UserID3"
        :param msg: "hello world!"

        :return: dict
                 {"errcode" : 0, "errmsg" : "ok"}
        """
        return self.send_msg(touser=touser, msgtype='text', content={'content': msg})

    def send_text_toparty(self, toparty: str, msg: str):
        """
        发送消息给同事

        :param toparty:  "PartyID1|PartyID2"
        :param msg: "hello world!"

        :return: dict
                 {"errcode" : 0, "errmsg" : "ok"}
        """
        return self.send_msg(toparty=toparty, msgtype='text', content={'content': msg})

    def send_text_totag(self, totag: str, msg: str):
        """
        发送消息给同事

        :param totag: "TagID1|TagID2"
        :param msg: "hello world!"

        :return: dict
                 {"errcode" : 0, "errmsg" : "ok"}
        """
        return self.send_msg(totag=totag, msgtype='text', content={'content': msg})

    def send_img(self, touser: str = '', toparty: str = '', totag: str = '', media_id='') -> dict:
        """发送图片消息

        Parameters
        ----------
            touser :
                "UserID1|UserID2|UserID3"
            toparty :
                "PartyID1|PartyID2"
            totag :
                "TagID1|TagID2"
            img_file:
                图片文件

        Returns
        -------
        result : dict
            返回示例
            {
                "errcode" : 0,
                "errmsg" : "ok",
                "invaliduser" : "userid1|userid2", // 不区分大小写，返回的列表都统一转为小写
                "invalidparty" : "partyid1|partyid2",
                "invalidtag":"tagid1|tagid2"
            }
        """
        return self.send_msg(touser, toparty, totag, msgtype='image', content={'media_id': media_id})

    def send_msg(self, touser: str = '', toparty: str = '', totag: str = '', msgtype: str = 'text', content: dict = {}) -> dict:
        """
        发送消息

        Parameters
        ----------
        touser : str, default ''
            用户
        toparty : str, default ''
            部门
        totag : str, default ''
            标签
        msgtype : str, default 'text'
            消息类型
        content :
            内容

        Returns
        -------
        result : dict 返回示例
            {
                "errcode" : 0,
                "errmsg" : "ok",
                "invaliduser" : "userid1|userid2", // 不区分大小写，返回的列表都统一转为小写
                "invalidparty" : "partyid1|partyid2",
                "invalidtag":"tagid1|tagid2"
            }
            如果部分接收人无权限或不存在，发送仍然执行，但会返回无效的部分（即invaliduser或invalidparty或invalidtag），常见的原因是接收人不在应用的可见范围内。

        Notes
        -----
        touser、toparty、totag不能同时为空，后面不再强调。

        Examples
        --------
        应用支持推送文本、图片、视频、文件、图文等类型

        >>> msgtype : text 文本消息
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1|PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "text",
           "agentid" : 1,
           "text" : {
               "content" : "你的快递已到，请携带工卡前往邮件中心领取。\\n出发前可查看<a href=\"http://work.weixin.qq.com\">邮件中心视频实况</a>，聪明避开排队。"
           },
           "safe":0
        }
        参数说明：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：text
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            content	是	消息内容，最长不超过2048个字节，超过将截断
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0
        特殊说明：
            其中text参数的content字段可以支持换行、以及A标签，即可打开自定义的网页（可参考以上示例代码）(注意：换行符请用转义过的\\n)

        >>> msgtype : image 图片消息
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1|PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "image",
           "agentid" : 1,
           "image" : {
                "media_id" : "MEDIA_ID"
           },
           "safe":0
        }
        请求参数：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：image
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            media_id	是	图片媒体文件id，可以调用上传临时素材接口获取
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0

        >>> msgtype : voice 语音消息
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1|PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "voice",
           "agentid" : 1,
           "voice" : {
                "media_id" : "MEDIA_ID"
           }
        }
        参数说明：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：voice
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            media_id	是	语音文件id，可以调用上传临时素材接口获取

        >>> msgtype : video 视频消息
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1|PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "video",
           "agentid" : 1,
           "video" : {
                "media_id" : "MEDIA_ID",
                "title" : "Title",
               "description" : "Description"
           },
           "safe":0
        }
        参数说明：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：video
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            media_id	是	视频媒体文件id，可以调用上传临时素材接口获取
            title	否	视频消息的标题，不超过128个字节，超过会自动截断
            description	否	视频消息的描述，不超过512个字节，超过会自动截断
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0

        >>> msgtype : file 文件消息
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1|PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "file",
           "agentid" : 1,
           "file" : {
                "media_id" : "1Yv-zXfHjSjU-7LH-GwtYqDGS-zz6w22KmWAT5COgP7o"
           },
           "safe":0
        }
        参数说明：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：file
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            media_id	是	文件id，可以调用上传临时素材接口获取
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0

        >>> msgtype : textcard 文本卡片消息
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1 | PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "textcard",
           "agentid" : 1,
           "textcard" : {
                    "title" : "领奖通知",
                    "description" : "<div class=\"gray\">2016年9月26日</div> <div class=\"normal\">恭喜你抽中iPhone 7一台，领奖码：xxxx</div><div class=\"highlight\">请于2016年10月10日前联系行政同事领取</div>",
                    "url" : "URL",
                    "btntxt":"更多"
           }
        }
        参数说明：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：textcard
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            title	是	标题，不超过128个字节，超过会自动截断
            description	是	描述，不超过512个字节，超过会自动截断
            url	是	点击后跳转的链接。
            btntxt	否	按钮文字。 默认为“详情”， 不超过4个文字，超过自动截断。
        特殊说明：
            卡片消息的展现形式非常灵活，支持使用br标签或者空格来进行换行处理，也支持使用div标签来使用不同的字体颜色，目前内置了3种文字颜色：灰色(gray)、高亮(highlight)、默认黑色(normal)，将其作为div标签的class属性即可，具体用法请参考上面的示例。

        >>> msgtype : news 图文消息
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1 | PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "news",
           "agentid" : 1,
           "news" : {
               "articles" : [
                   {
                       "title" : "中秋节礼品领取",
                       "description" : "今年中秋节公司有豪礼相送",
                       "url" : "URL",
                       "picurl" : "http://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png"
                   }
                ]
           }
        }
        参数说明：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：news
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            articles	是	图文消息，一个图文消息支持1到8条图文
            title	是	标题，不超过128个字节，超过会自动截断
            description	否	描述，不超过512个字节，超过会自动截断
            url	是	点击后跳转的链接。
            picurl	否	图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。

        >>> msgtype : mpnews 图文消息
        mpnews类型的图文消息，跟普通的图文消息一致，唯一的差异是图文内容存储在企业微信。
        多次发送mpnews，会被认为是不同的图文，阅读、点赞的统计会被分开计算。
        请求示例：
        {
           "touser" : "UserID1|UserID2|UserID3",
           "toparty" : "PartyID1 | PartyID2",
           "totag": "TagID1 | TagID2",
           "msgtype" : "mpnews",
           "agentid" : 1,
           "mpnews" : {
               "articles":[
                   {
                       "title": "Title",
                       "thumb_media_id": "MEDIA_ID",
                       "author": "Author",
                       "content_source_url": "URL",
                       "content": "Content",
                       "digest": "Digest description"
                    }
               ]
           },
           "safe":0
        }
        参数说明：
            参数	是否必须	说明
            touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：mpnews
            agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
            articles	是	图文消息，一个图文消息支持1到8条图文
            title	是	标题，不超过128个字节，超过会自动截断
            thumb_media_id	是	图文消息缩略图的media_id, 可以通过素材管理接口获得。此处thumb_media_id即上传接口返回的media_id
            author	否	图文消息的作者，不超过64个字节
            content_source_url	否	图文消息点击“阅读原文”之后的页面链接
            content	是	图文消息的内容，支持html标签，不超过666 K个字节
            digest	否	图文消息的描述，不超过512个字节，超过会自动截断
            safe	否	表示是否是保密消息，0表示可对外分享，1表示不能分享且内容显示水印，2表示仅限在企业内分享，默认为0；注意仅mpnews类型的消息支持safe值为2，其他消息类型不支持

        """

        params: dict = {
            'touser': touser,
            'toparty': toparty,
            'totag': totag,
            'msgtype': msgtype,
            'agentid': self.agent_id,
            'safe': 0
        }
        params[msgtype] = content
        result = self._request(c.POST, c.SEND_MSG, params)
        return result

    def upload_tmp(self, file_name: str) -> dict:
        """上传临时素材

        :param file_name:
            文件名
                普通文件	application/octet-stream
                jpg图片	image/jpg
                png图片	image/png
                bmp图片	image/bmp
                amr音频	voice/amr
                mp4视频	video/mp4

        :return: dict
            {
               "errcode": 0,
               "errmsg": ""，
               "type": "image",
               "media_id": "1G6nrLmr5EC3MMb_-zK1dDdzmd0p7cNliYu9V5w7o8K0",
               "created_at": "1380000000"
            }
        """
        ext = os.path.splitext(file_name)
        if len(ext) > 1:
            ext = ext[1][1:]
            if ext in ['jpg', 'png', 'bmp']:
                type = 'image'
                content_type = '{}/{}'.format(type, ext)
            elif ext in ['amr']:
                type = 'voice'
                content_type = '{}/{}'.format(type, ext)
            elif ext in ['mp4']:
                type = 'video'
                content_type = '{}/{}'.format(type, ext)
            else:
                type = 'file'
                content_type = 'application/octet-stream'
        else:
            type = 'file'
            content_type = 'application/octet-stream'

        bs = open(file_name, 'rb').read()

        # file中的第一个参数应为文件名, 但不能是中文, 故此处采用type替代亦可
        m = MultipartEncoder({'name': 'media', 'filename': os.path.split(file_name)[1], 'file': ('name_no_cn', bs, content_type)})

        header: dict = {}
        header[c.CONTENT_TYPE] = m.content_type
        result = self._request(c.POST, c.UPLOAD_TMP, params='', add_path={'type': type}, add_header=header, data=m)
        return result

    def create_menu(self, id: str, name: str):

        self._request(c.GET, c.DELETE_MENU)

        json_str = '''
{{
   "button":[
       {{    
           "name":"{name}",
           "sub_button":[
            {{
                "type":"click",
                "name":"name",
                "key":"{key}"
            }}
           ]
       }}
   ]
}}'''.format(key=id, name=name).encode('utf-8')
        return self._request(c.POST, c.CREATE_MENU, data=json_str)

    def _request(self, method, request_path, params: dict = {}, add_path: dict = {}, add_header: dict = {}, data=None) -> dict:
        """
        发送请求

        :param method: c.GET or c.POST
        :param request_path: 请求路径
        :type request_path: dict
        :param params: 请求参数
        :return: result of dict
        """
        # url 中增加 access_token 参数
        if len(self.access_token) > 0:
            request_path += f'?access_token={self.access_token}&agentid={self.agent_id}'
        for k, v in add_path.items():
            request_path += '&{}={}'.format(k, v)
        if method == c.GET:
            if len(self.access_token) > 0:
                request_path += '&' + utils.parse_params_to_str(params)[1:]  # 用&替换掉?
            else:
                request_path = request_path + utils.parse_params_to_str(params)
        # url
        url = c.API_URL + request_path

        timestamp = utils.get_timestamp()

        body = json.dumps(params, ensure_ascii=False).encode('utf-8') if method == c.POST else ""

        # header = utils.get_header(timestamp)
        # # 两个dict相连, 后面覆盖前面
        # header = {**header, **add_header}
        header = add_header

        # send request
        response = None
        # print("url:", url)
        # print("headers:", header)
        # print("body:", body)
        if method == c.GET:
            response = requests.get(url, headers=header)
        elif method == c.POST:
            if data is None:
                response = requests.post(url, data=body, headers=header)
            else:
                response = requests.post(url, headers=header, data=data)
            # response = requests.post(url, json=body, headers=header)
        elif method == c.DELETE:
            response = requests.delete(url, headers=header)

        # exception handle
        if not str(response.status_code).startswith('2'):
            raise exceptions.WorkException(response)
        try:
            res_header = response.headers
            rtn = response.json()
            if rtn['errcode'] == 0:
                return rtn
            raise exceptions.WorkException(response)
        except ValueError:
            raise exceptions.WorkRequestException('Invalid Response: {}'.format(response.text))
