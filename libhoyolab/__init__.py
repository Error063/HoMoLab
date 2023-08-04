# encoding:utf-8
import hashlib
import pprint
import string
import time
import random

import urllib3
import json
import requests
from libhoyolab import threadRender, accountLogin, urls

_USERAGENT = 'Mozilla/5.0 (Linux; Android 13; M2101K9C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/108.0.5359.128 Mobile Safari/537.36 miHoYoBBS/2.51.1'

urllib3.disable_warnings()

headers = {
    "User-Agent": _USERAGENT,
    "x-rpc-sys_version": "13",
    "x-rpc-channel": "xiaomi",
    "x-rpc-device_name": "Xiaomi M2101K9C",
    "X-Requested-With": "com.mihoyo.hyperion",
    "x-rpc-app_id": "bll8iq97cem8",
    "Referer": "https://app.mihoyo.com",
    "X-Rpc-App_version": "2.55.1",
    "Ds": "",
    "Dnt": "1",
    "X-Rpc-Client_type": "4",
    "Cookie": ''
}
cookie_dict = dict()
newsType = {'announce': '1', 'activity': '2', 'information': '3'}

session = requests.session()


def get_ds():
    def md5(text: str) -> str:
        _md5 = hashlib.md5()
        _md5.update(text.encode())
        return _md5.hexdigest()

    n = "F6tsiCZEIcL9Mor64OXVJEKRRQ6BpOZa"
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    headers["Ds"] = f"{i},{r},{c}"


def login():
    global cookie_dict, headers
    cookie = accountLogin.login()
    while "cookie_token_v2" not in cookie[0].lower():
        cookie = accountLogin.login()
    headers['Cookie'] = cookie[0]
    get_ds()


def getEmotions(gid='2'):
    print('emotion lib is running')
    emotionDict = dict()
    req = session.get(urls.emoticon_set.format(str(gid)), verify=False)
    contents = json.loads(req.content.decode("utf8"))['data']['list']

    for emotionSet in contents:
        for emotion in emotionSet['list']:
            emotionDict[emotion['name']] = emotion['icon']

    return emotionDict


class Article:
    def __init__(self, post_id):
        print(f'getting article from {post_id}')
        print('accessing ' + urls.getPostFull.format(str(post_id)))
        count = 3
        while count != 0:
            try:
                req = session.get(urls.getPostFull.format(str(post_id)), headers=headers, verify=False)
                break
            except:
                count -= 1
                continue
        if count == 0:
            raise Exception('Connection Failed!')
        self.result = json.loads(req.content.decode("utf8"))

    def getRaw(self):
        return self.result

    def getPostId(self):
        return self.result["data"]['post']['post']['post_id']

    def getGameId(self):
        return str(self.result["data"]['post']['post']['game_id'])

    def getContent(self):
        return threadRender.replaceEmotions(self.result["data"]['post']['post']['content'],
                                            emotionDict=getEmotions(gid=self.getGameId()))

    def getRenderType(self):
        return self.result["data"]['post']['post']['view_type']

    def getStructuredContent(self, rendered=True):
        structured = self.result["data"]["post"]["post"]["structured_content"]
        if len(structured) > 0:
            if rendered:
                return threadRender.render(json.loads(structured), emotionDict=getEmotions(gid=self.getGameId()))
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

    def getTags(self):
        tags = list()
        for tag in self.result['data']['post']['topics']:
            tags.append({
                'name': tag['name'],
                'cover': tag['cover'],
                'id': tag['id']
            })
        return tags


class Page:
    def __init__(self, gid, pageType, page=1, pageSize=50):
        print('getting page')
        if pageType == 'recommend':
            apiUrl = urls.webHome.format(str(gid), str(page), str(pageSize))
        else:
            if pageType not in newsType:
                typeNum = '1'
            else:
                typeNum = newsType[pageType]
            apiUrl = urls.getNewsList.format(str(gid), str(typeNum), str(pageSize),
                                             str((int(page) - 1) * 50 + 1))
        print('accessing ' + apiUrl)
        count = 3
        while count != 0:
            try:
                req = session.get(apiUrl, headers=headers, verify=False)
                break
            except:
                count -= 1
                continue
        if count == 0:
            raise Exception('Connection Failed!')
        result = json.loads(req.content.decode("utf8"))
        self.articles = list()
        for articleInfo in result['data']['recommended_posts' if pageType == 'recommend' else 'list']:
            try:
                if articleInfo['post']['view_type'] not in [1, 2]:
                    continue
                article = dict()
                article['post_id'] = articleInfo['post']['post_id']
                article['title'] = articleInfo['post']['subject']
                article['describe'] = articleInfo['post']['content'][:50] + str(
                    "..." if len(articleInfo['post']['content']) > 50 else '')
                article['cover'] = articleInfo['post']['images'][0] if articleInfo['post']['cover'] == "" else \
                    articleInfo['post']['cover']
                article['authorAvatar'] = articleInfo['user']['avatar_url']
                article['authorName'] = articleInfo['user']['nickname']
                describe = articleInfo['user']['certification']['label'] if len(
                    articleInfo['user']['certification']['label']) > 0 else articleInfo['user']['introduce'][
                                                                            :15] + '...' if len(
                    articleInfo['user']['introduce']) > 15 else ''
                article['authorDescribe'] = describe
                article['type'] = articleInfo['post']['view_type']

                self.articles.append(article)
            except:
                continue

    def getArticles(self):
        return self.articles


class Comments:
    def __init__(self, post_id, gid, page=1, max_size=20, rank_by_hot=True, orderby=1):
        self.page = int(page)
        self.post_id = post_id
        self.gid = gid
        start = (int(page) - 1) * int(max_size) + 1
        print(f"getting comments from {post_id}, start from {start}")
        self.rank_by_hot = rank_by_hot
        self.comments = []
        comments: list = [None] * (max_size + 1) if rank_by_hot else [None] * max_size
        self.have_top = False
        gid = str(gid)
        emotionDict = getEmotions(gid)
        print("accessing " + urls.getPostReplies.format(str(gid), str(rank_by_hot).lower(), str(post_id), str(max_size),
                                                        str(start), str(orderby)))
        count = 3
        while count != 0:
            try:
                req = session.get(
                    urls.getPostReplies.format(str(gid), str(rank_by_hot).lower(), str(post_id), str(max_size),
                                               str(start),str(orderby)),
                    headers=headers, verify=False, stream=True)
                break
            except:
                count -= 1
                continue
        if count == 0:
            raise Exception('Connection Failed!')
        result = json.loads(req.content.decode("utf8"))
        self.isLastFlag = result['data']['is_last']
        comments_raw = result['data']['list']
        for i in range(len(comments_raw)):
            reply = comments_raw[i]
            tmp = {
                'floor_id': reply['reply']['floor_id'],
                'post_id': reply['reply']['post_id'],
                'content': threadRender.replaceEmotions(reply['reply']['content'], emotionDict=emotionDict),
                'username': reply['user']['nickname'],
                'avatar': reply['user']['avatar_url'],
                'describe': reply['user']['certification']['label'] if len(
                    reply['user']['certification']['label']) > 0 else reply['user']['introduce']
            }
            if rank_by_hot:
                if reply['reply']:
                    comments[0] = tmp
                else:
                    comments[i + 1] = tmp
            else:
                comments[i] = tmp
            for reply in comments:
                if reply is not None:
                    self.comments.append(reply)

    def getComments(self):
        return self.comments

    def getSubComments(self):
        return


def debug():
    login()
    pprint.pprint(headers)
    a = requests.get(f"https://bbs-api.miyoushe.com/user/api/getUserFullInfo", headers=headers)
    print(a.cookies.get_dict())
    j = a.json()
    pprint.pprint(j)
