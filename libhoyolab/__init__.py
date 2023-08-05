# encoding:utf-8
import hashlib
import os.path
import string
import time
import random
import uuid

import urllib3
import json
import requests
from libhoyolab import threadRender, accountLogin, urls
import logging

urllib3.disable_warnings()

Salt_Sign = 'PVeGWIZACpxXZ1ibMVJPi9inCY4Nd4y2'  # 米游社签到salt
Salt_BBS = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'  # 米游社讨论区专用salt
mysVersion = "2.38.1"  # 米游社版本
mysClient_type = '2'  # 1:ios 2:Android

account_dir = './configs/account.json'

if os.path.exists(account_dir):
    with open(account_dir) as f:
        account = json.load(f)
else:
    account = {"isLogging": False, "login_ticket": "", "stuid": "", "stoken": ""}
    with open(account_dir, mode='w') as f:
        json.dump(account, f)

_USERAGENT = 'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/105.0.5195.79 Mobile Safari/537.36 miHoYoBBS/2.38.1'
login_ticket = account["login_ticket"]
stuid = account["stuid"]
stoken = account["stoken"]
cookie = f'login_ticket={login_ticket}'

newsType = {'announce': '1', 'activity': '2', 'information': '3'}
gamesById = ['bh3', 'ys', 'bh2', 'wd', 'dby', 'sr', '', 'zzz']

session = requests.session()


def md5(text):
    '''md5加密'''
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


def randomStr(n):
    '''生成指定位数的随机数'''
    return (''.join(random.sample(string.digits + string.ascii_letters, n))).lower()


def DS_BBS():
    '''生成米游社DS'''
    n = Salt_Sign
    i = str(int(time.time()))
    r = randomStr(6)
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return "{},{},{}".format(i, r, c)


def headerGenerate(app='web', withCookie=True, withDs=True):
    headers = {
        "Cookie": f'login_ticket={login_ticket};stuid={stuid};stoken={stoken}' if withCookie else '',
        'User-Agent': "okhttp/4.8.0" if app == 'app' else _USERAGENT,
        "Dnt": "1",
        "DS": DS_BBS() if withDs else '',  # 随用随更新，保证实时性
        "x-rpc-client_type": '2' if app == 'app' else '4',
        "x-rpc-app_version": mysVersion,
        "X-Requested-With": "com.mihoyo.hyperion",
        "x-rpc-device_id": str(uuid.uuid3(uuid.NAMESPACE_URL, cookie)),
        "x-rpc-device_name": "vivo s7",
        "x-rpc-device_model": "vivo-s7",
        "x-rpc-sys_version": "12",
        "x-rpc-channel": "bll8iq97cem8",
        # "Accept-Encoding": "gzip",
        "Referer": "https://app.mihoyo.com",
        # "Host": "bbs-api.mihoyo.com"
    }
    return headers


def getEmotions(gid='2'):
    logging.info('emotion lib is running')
    emotionDict = dict()
    req = session.get(urls.emoticon_set.format(str(gid)), verify=False)
    contents = json.loads(req.content.decode("utf8"))['data']['list']

    for emotionSet in contents:
        for emotion in emotionSet['list']:
            emotionDict[emotion['name']] = emotion['icon']

    return emotionDict


class Article:
    def __init__(self, post_id):
        logging.info(f'getting article from {post_id}')
        logging.info('accessing ' + urls.getPostFull.format(str(post_id)))
        count = 3
        while count != 0:
            try:

                req = session.get(urls.getPostFull.format(str(post_id)), headers=headerGenerate(app='web'),
                                  verify=False, timeout=3)
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
        return threadRender.replaceAll(self.result["data"]['post']['post']['content'],
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
        self.page = page
        logging.info('getting page')
        if pageType == 'recommend':
            apiUrl = urls.webHome.format(str(gid), str(page), str(pageSize))
        else:
            if pageType not in newsType:
                typeNum = '1'
            else:
                typeNum = newsType[pageType]
            apiUrl = urls.getNewsList.format(str(gid), str(typeNum), str(pageSize),
                                             str((int(page) - 1) * 50 + 1))
        logging.info('accessing ' + apiUrl)
        logging.debug(headerGenerate(app='web'))
        count = 3
        err = None
        while count != 0:
            try:

                req = session.get(apiUrl, headers=headerGenerate(app='web'), verify=False, timeout=3)
                break
            except Exception as e:
                err = e
                count -= 1
                continue
        if count == 0:
            raise Exception(f'Connection Failed! {err}')
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
        logging.info(f"getting comments from {post_id}, start from {start}")
        self.rank_by_hot = rank_by_hot
        self.comments = []
        comments: list = [None] * (max_size + 1) if rank_by_hot else [None] * max_size
        self.have_top = False
        gid = str(gid)
        emotionDict = getEmotions(gid)
        logging.info(
            "accessing " + urls.getPostReplies.format(str(gid), str(rank_by_hot).lower(), str(post_id), str(max_size),
                                                      str(start), str(orderby)))
        count = 3
        while count != 0:
            try:
                #
                req = session.get(
                    urls.getPostReplies.format(str(gid), str(rank_by_hot).lower(), str(post_id), str(max_size),
                                               str(start), str(orderby)),
                    headers=headerGenerate(app='web'), verify=False, stream=True, timeout=3)
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
                'content': threadRender.replaceAll(reply['reply']['content'], emotionDict=emotionDict),
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


class Search:
    def __init__(self, keyWords, gid, page=1, max_size=20):
        self.gid = gid
        start = int(page)
        logging.info(f'searching {keyWords}, from {start}')
        logging.info(f'accessing {urls.searchPosts.format(str(gid), str(keyWords), str(start), str(max_size))}')
        count = 3
        while count != 0:
            try:
                req = session.get(
                    urls.searchPosts.format(str(gid), str(keyWords), str(start), str(max_size)),
                    headers=headerGenerate(app='web'), verify=False, stream=True, timeout=3)
                break
            except:
                count -= 1
                continue
        if count == 0:
            raise Exception('Connection Failed!')
        result = json.loads(req.content.decode("utf8"))
        self.isLastFlag = result['data']['is_last']
        self.articles = list()
        for articleInfo in result['data']['posts']:
            # logging.info(articleInfo['post']['subject'])
            # if articleInfo['post']['view_type'] not in [1, 2]:
            #     continue
            article = dict()
            article['post_id'] = articleInfo['post']['post_id']
            article['title'] = articleInfo['post']['subject']
            article['describe'] = articleInfo['post']['content'][:50] + str(
                "..." if len(articleInfo['post']['content']) > 50 else '')
            try:
                article['cover'] = articleInfo['post']['cover'] if articleInfo['post']['cover'] != "" else \
                    articleInfo['post']['images'][0]
            except:
                article['cover'] = ''
            article['authorAvatar'] = articleInfo['user']['avatar_url']
            article['authorName'] = articleInfo['user']['nickname']
            describe = articleInfo['user']['certification']['label'] if len(
                articleInfo['user']['certification']['label']) > 0 else articleInfo['user']['introduce'][
                                                                        :15] + '...' if len(
                articleInfo['user']['introduce']) > 15 else ''
            article['authorDescribe'] = describe
            article['type'] = articleInfo['post']['view_type']

            self.articles.append(article)

    def getArticles(self):
        return self.articles


def login():
    global cookie, login_ticket, stuid, stoken, account
    with open(account_dir) as f:
        login_ticket = json.load(f)['login_ticket']
    resp = requests.get(url=urls.Cookie_url.format(login_ticket))
    data = json.loads(resp.text.encode('utf-8'))
    logging.debug(str(data))
    if "成功" in data["data"]["msg"]:
        stuid = data["data"]["cookie_info"]["account_id"]
        resp = requests.get(url=urls.Cookie_url2.format(login_ticket, stuid))  # 获取stoken
        # print(response.text)
        data = json.loads(resp.text.encode('utf-8'))
        stoken = data["data"]["list"][0]["token"]
        account = {"isLogging": True, "login_ticket": login_ticket, "stuid": stuid, "stoken": stoken}
        logging.debug("tokens: " + str(account))
        with open(account_dir, mode='w') as f:
            json.dump(account, f)


def logout():
    global account, cookie, login_ticket, stuid, stoken
    os.unlink(account_dir)
    cookie = ''
    login_ticket = ''
    stuid = ''
    stoken = ''
    account = {"isLogging": False, "login_ticket": "", "stuid": "", "stoken": ""}
    with open(account_dir, mode='w') as f:
        json.dump(account, f)


class Account:
    def __init__(self):
        resp = requests.get(f"https://bbs-api.miyoushe.com/user/api/getUserFullInfo",
                            headers=headerGenerate(app='web', withCookie=True, withDs=True))
        info = resp.json()
        logging.debug(str(info))
        if info['retcode'] == -100:
            self.indo = dict()
            self.isLogging = False
        else:
            self.info = info['data']
            self.isLogging = True

    def getNickname(self):
        return self.info['user_info']['nickname'] if self.isLogging else '未登录'

    def getAvatar(self):
        return self.info['user_info'][
            'avatar_url'] if self.isLogging else 'https://img-static.mihoyo.com/communityweb/upload/c9d11674eac7631d2210a1ba20799958.png'
