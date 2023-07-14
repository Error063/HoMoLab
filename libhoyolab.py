import pprint

import accountLogin
import json
import requests
import threadRender

_USERAGENT = 'Mozilla/5.0 (Linux; Android 13; M2101K9C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/108.0.5359.128 Mobile Safari/537.36 miHoYoBBS/2.51.1'

import time
import random
from hashlib import md5
import urllib3
urllib3.disable_warnings()

lettersAndNumbers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

# 将要使用的salt，此为2.35.2版本的K2 salt。
salt = "ZSHlXeQUBis52qD1kEgKt5lUYed4b7Bb"

t = int(time.time())
r = "".join(random.choices(lettersAndNumbers, k=6))
main = f"salt={salt}&t={t}&r={r}"
ds = md5(main.encode(encoding='UTF-8')).hexdigest()

final = f"{t},{r},{ds}"  # 最终结果。

headers = {
    "User-Agent": _USERAGENT,
    "x-rpc-client_type": "5",
    "x-rpc-sys_version": "13",
    "x-rpc-channel": "xiaomi",
    "x-rpc-device_name": "Xiaomi M2101K9C",
    "X-Requested-With": "com.mihoyo.hyperion",
    "x-rpc-app_id": "bll8iq97cem8",
    "Referer": "https://webstatic.mihoyo.com",
    "Cookie": '',
    "SToken": '',
    "LToken": ''
}
cookie_dict = dict()

def login():
    global cookie_dict, headers
    cookie = accountLogin.login()
    while "login_ticket" not in cookie[0].lower():
        cookie = accountLogin.login()
    headers['Cookie'] = cookie[0]
    cookie_dict = cookie[1]
    tokens_raw = requests.get(f"https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={cookie_dict['login_ticket']}&token_types=3&uid={cookie_dict['login_uid']}", headers=headers).content.decode("utf8")
    tokens = json.loads(tokens_raw)['data']


class Article:
    def __init__(self, post_id):
        print(post_id)
        req = requests.get(f"https://bbs-api.miyoushe.com/post/api/getPostFull?post_id={post_id}", headers=headers, verify=False)
        self.result = json.loads(req.content.decode("utf8"))

    def getRaw(self):
        return self.result

    def getContent(self):
        return self.result["data"]['post']['post']['content']

    def getRenderType(self):
        return self.result["data"]['post']['post']['view_type']

    def getStructuredContent(self,rendered=True):
        structured = self.result["data"]["post"]["post"]["structured_content"]
        if len(structured) > 0:
            if rendered:
                return threadRender.render(json.loads(structured))
            else:
                return json.loads(self.result["data"]["post"]["post"]["structured_content"])
        else:
            return ''

    def getTitle(self):
        return self.result['data']['post']['post']['subject']

    def getAuthor(self):
        return self.result['data']['post']['user']['nickname']

    def getAuthorAvatar(self):
        return self.result['data']['post']['user']['avatar_url']

    def getAuthorDescribe(self):
        return f"{self.result['data']['post']['user']['certification']['label'] if len(self.result['data']['post']['user']['certification']['label']) > 0 else self.result['data']['post']['user']['introduce']}"

    def getImages(self):
        return self.result['data']['post']['post']['images']

class MainPage:
    def __init__(self, gid, page=1):
        print('working...')
        req = requests.get(f"https://bbs-api-static.miyoushe.com/apihub/wapi/webHome?gids={gid}&page={page}&page_size=50", headers=headers, verify=False)
        result = json.loads(req.content.decode("utf8"))
        self.articles = list()
        for articleInfo in result['data']['recommended_posts']:
            try:
                article = dict()
                article['post_id'] = articleInfo['post']['post_id']
                article['title'] = articleInfo['post']['subject']
                article['describe'] = articleInfo['post']['content'][:50] + str("..." if len(articleInfo['post']['content']) > 50 else '')
                article['cover'] = articleInfo['post']['images'][0] if articleInfo['post']['cover'] == "" else articleInfo['post']['cover']
                article['authorAvatar'] = articleInfo['user']['avatar_url']
                article['authorName'] = articleInfo['user']['nickname']
                describe = f"{articleInfo['user']['certification']['label'] if len(articleInfo['user']['certification']['label']) > 0 else articleInfo['user']['introduce']}"
                # describe = f"{articleInfo['user']['introduce']}"
                article['authorDescribe'] = describe
                article['type'] = articleInfo['post']['view_type']
                self.articles.append(article)
            except:
                continue

    def getArticles(self):
        return self.articles

if __name__ == '__main__':
    login()
    pprint.pprint(cookie_dict)
    # print(headers)
    # a = requests.get(f"https://bbs-api.miyoushe.com/post/api/getPostFull?post_id=41200597", headers=headers)
    # a = requests.get(f"https://bbs-api.miyoushe.com/user/api/getUserFullInfo", headers=headers)
    # a = requests.get(f"https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket=k7sepaAIkySyMKyRoYiQx5GcqISqzMYBfcRfpUBF&token_types=3&uid=311526738", headers=headers)
    # j = json.loads(a.content.decode("utf8"))
    # j['data']['post']['post']['structured_content'] = json.loads(j['data']['post']['post']['structured_content'])
    # with open(f"tests/result-{str(int(time.time()))}", mode="w", encoding="utf8") as f:
    #     json.dump(j, fp=f, ensure_ascii=False)




