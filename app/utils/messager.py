# -*- encoding: utf-8 -*-
'''
@File    :   messager.py
@Time    :   2023/03/12 14:27:33
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse

D_TOKEN = "test_token"
D_SECRET = "test_secret"


class MessageTool:

    def __init__(self, token=D_TOKEN, secret=D_SECRET):
        self.token = token
        self.secret = secret

    @classmethod
    def get_object(cls, token: str, secret: str):
        return MessageTool(token, secret)
    
    def send_warn_message(self, text):
        headers = {"Content-Type": "application/json;charset=utf-8"}
        sign = self.get_sign() 
        api_url =  "https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%s&sign=%s" % (self.token, sign[0], sign[1])
        json_text = self._msg(text)
        return requests.post(api_url, data=json.dumps(json_text), headers=headers).content
    
    def get_sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return [timestamp, sign]
    
    @staticmethod
    def _msg(text):
        json_text = {
            "msgtype": "text",
            "at": {
                "atMobiles": [],
                "isAtAll": False
            },
            "text": {
                "content": text
            }
        }
        return json_text
    
    