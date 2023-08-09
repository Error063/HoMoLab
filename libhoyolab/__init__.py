# encoding:utf-8
import hashlib
import os.path
import pprint
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

Salt_LK2 = 'PVeGWIZACpxXZ1ibMVJPi9inCY4Nd4y2'  # 米游社签到salt
Salt_K2 = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'  # 米游社讨论区专用salt
# Salt_LK2 = 'F6tsiCZEIcL9Mor64OXVJEKRRQ6BpOZa'  # 米游社签到salt
# Salt_K2 = 'xc1lzZFOBGU0lz8ZkPgcrWZArZzEVMbA'  # 米游社讨论区专用salt
Salt_4X = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs	'
Salt_6X = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'
mysVersion = "2.38.1"  # 米游社版本
# mysVersion = '2.55.1'
mysClient_type = '2'  # 1:ios 2:Android

account_dir = './configs/account.json'

if not os.path.exists(account_dir + "/.."):
    os.mkdir(account_dir + "/..")

if os.path.exists(account_dir):
    with open(account_dir) as f:
        account = json.load(f)
else:
    account = {"isLogin": False, "login_ticket": "", "stuid": "", "stoken": ""}
    with open(account_dir, mode='w') as f:
        json.dump(account, f)

_USERAGENT = f'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/105.0.5195.79 Mobile Safari/537.36 miHoYoBBS/{mysVersion}'
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


def DS1():
    '''生成米游社DS'''
    n = Salt_LK2
    i = str(int(time.time()))
    r = randomStr(6)
    c = md5(f"salt={n}&t={i}&r={r}")
    return "{},{},{}".format(i, r, c)


def DS2(query='', body='', salt='4x'):
    salt = Salt_4X if salt.lower() == '4x' else Salt_6X
    new_body = dict()
    if not body:
        if type(body) is str:
            body = json.loads(body)
            for key in sorted(json.loads(body)):
                new_body[key] = body[key]
            body = json.dumps(new_body)
        elif type(body) is dict:
            for key in sorted(body):
                new_body[key] = body[key]
            body = json.dumps(new_body)
    if not query:
        query = '&'.join(sorted(query.split('&')))
    t = int(time.time())
    r = random.randint(100001, 200000)
    main = f"salt={salt}&t={t}&r={r}&b={body}"  # &q={query}
    ds = md5(main)
    return f"{t},{r},{ds}"


def headerGenerate(app='web', client='4', withCookie=True, withDs=True, agro=1, query='', body: str | dict = '{}',
                   salt='4x', Referer="https://www.miyoushe.com/"):
    headers = {
        "Cookie": f'login_ticket={login_ticket};stuid={stuid};stoken={stoken}' if withCookie and account[
            'isLogin'] else '',
        'User-Agent': "okhttp/4.8.0" if app == 'app' else _USERAGENT,
        "Dnt": "1",
        "DS": DS1() if agro == 1 else DS2(query, body, salt),
        "x-rpc-client_type": client,
        "x-rpc-app_version": mysVersion,
        "X-Requested-With": "com.mihoyo.hyperion",
        "x-rpc-device_id": str(uuid.uuid3(uuid.NAMESPACE_URL, cookie)),
        "x-rpc-device_name": "vivo s7",
        "x-rpc-device_model": "vivo-s7",
        "x-rpc-sys_version": "12",
        "x-rpc-channel": "miyousheluodi",
        "x-rpc-verify_key": "bll8iq97cem8",
        "Referer": Referer,
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


def articleSet(raw_articles: list, method: str='normal') -> list:
    articles = list()
    for articleInfo in raw_articles:
        article = dict()
        if method == 'history':
            articleInfo = articleInfo['post']
        article['post_id'] = articleInfo['post']['post_id']
        article['title'] = articleInfo['post']['subject']
        article['describe'] = articleInfo['post']['content'][:50] + str(
            "..." if len(articleInfo['post']['content']) > 50 else '')
        try:
            article['cover'] = articleInfo['post']['images'][0] if articleInfo['post']['cover'] == "" else \
                articleInfo['post']['cover']
        except:
            article['cover'] = ''
        article['authorAvatar'] = articleInfo['user']['avatar_url']
        article['uid'] = int(articleInfo['user']['uid'])
        article['authorName'] = articleInfo['user']['nickname']
        describe = articleInfo['user']['certification']['label'] if len(
            articleInfo['user']['certification']['label']) > 0 else articleInfo['user']['introduce'][
                                                                    :15] + '...' if len(
            articleInfo['user']['introduce']) > 15 else ''
        article['authorDescribe'] = describe
        article['type'] = articleInfo['post']['view_type']
        articles.append(article)

    return articles


def connectApi(apiUrl: str, method='get', data=None, headers=None) -> requests.Response:
    if headers is None:
        headers = headerGenerate(app='web')
    if data is None:
        data = {}
    count = 3
    err = None
    resp = None
    while count != 0:
        try:
            match method.lower():
                case 'get':
                    resp = session.get(url=apiUrl, headers=headers, verify=False, timeout=3)
                case 'post':
                    resp = session.post(url=apiUrl, headers=headers, json=data, verify=False, timeout=3)
                case _:
                    raise Exception('method not matched!')
            break
        except Exception as e:
            err = e
            count -= 1
            continue
    if count == 0:
        raise Exception(f'Connection Failed! {err}')
    return resp


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

    def getSelfAttitude(self):
        return bool(self.result['data']['post']['self_operation']['attitude'])

    def getVotes(self):
        return self.result['data']['post']['stat']['like_num']

    def getAuthorAvatar(self):
        return self.result['data']['post']['user']['avatar_url']

    def getAuthorUid(self):
        return int(self.result['data']['post']['user']['uid'])

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
        elif pageType == 'feeds':
            apiUrl = urls.feedPosts.format(str(gid), str(page))
        else:
            if pageType not in newsType:
                typeNum = '1'
            else:
                typeNum = newsType[pageType]
            apiUrl = urls.getNewsList.format(str(gid), str(typeNum), str(pageSize),
                                             str((int(page) - 1) * 50 + 1))
        logging.info('accessing ' + apiUrl)
        req = connectApi(apiUrl)
        logging.debug(req.text)
        result = req.json()
        self.articles = articleSet(result['data']['recommended_posts' if pageType == 'recommend' else 'list'])


class Comments:
    def __init__(self, post_id, gid, page=1, max_size=20, rank_by_hot=True, orderby=1):
        self.page = int(page)
        self.post_id = post_id
        self.gid = str(gid)
        start = (int(page) - 1) * int(max_size) + 1
        logging.info(f"getting comments from {post_id}, start from {start}")
        emotionDict = getEmotions(gid)
        apiUrl = urls.getPostReplies.format(str(gid), str(rank_by_hot).lower(), str(post_id), str(max_size),
                                            str(start), str(orderby))
        logging.info("accessing " + apiUrl)
        req = connectApi(apiUrl)
        result = req.json()

        self.rank_by_hot = rank_by_hot
        self.comments = []
        comments: list = [None] * (max_size + 1) if rank_by_hot else [None] * max_size
        self.have_top = False
        self.isLastFlag = result['data']['is_last']
        comments_raw = result['data']['list']
        for i in range(len(comments_raw)):
            reply = comments_raw[i]
            tmp = {
                'floor_id': reply['reply']['floor_id'],
                'post_id': reply['reply']['post_id'],
                'content': threadRender.replaceAllFromDelta(reply['reply']['struct_content'], emotionDict),
                'username': reply['user']['nickname'],
                'uid': int(reply['user']['uid']),
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


    # def getSubComments(self):
    #     return


class Search:
    def __init__(self, keyWords, gid, page=1, max_size=20):
        self.gid = gid
        start = int(page)
        logging.info(f'searching {keyWords}, from {start}')
        logging.info(f'accessing {urls.searchPosts.format(str(gid), str(keyWords), str(start), str(max_size))}')
        req = connectApi(apiUrl=urls.searchPosts.format(str(gid), str(keyWords), str(start), str(max_size)))
        result = req.json()
        self.isLastFlag = result['data']['is_last']
        self.articles = articleSet(result['data']['posts'])

    def getArticles(self):
        return self.articles


def login():
    global cookie, login_ticket, stuid, stoken, account
    with open(account_dir) as f:
        login_ticket = json.load(f)['login_ticket']
    resp = session.get(url=urls.Cookie_url.format(login_ticket))
    data = json.loads(resp.text.encode('utf-8'))
    logging.debug(str(data))
    if "成功" in data["data"]["msg"]:
        stuid = data["data"]["cookie_info"]["account_id"]
        resp = session.get(url=urls.Cookie_url2.format(login_ticket, stuid))  # 获取stoken
        print(resp.text)
        data = json.loads(resp.text.encode('utf-8'))
        stoken = data["data"]["list"][0]["token"]
        account = {"isLogin": True, "login_ticket": login_ticket, "stuid": stuid, "stoken": stoken}
        logging.debug("tokens: " + str(account))
        with open(account_dir, mode='w') as f:
            json.dump(account, f)
    else:
        print(f'failed, {data}')


def logout():
    global account, cookie, login_ticket, stuid, stoken
    os.unlink(account_dir)
    cookie = ''
    login_ticket = ''
    stuid = ''
    stoken = ''
    account = {"isLogin": False, "login_ticket": "", "stuid": "", "stoken": ""}
    with open(account_dir, mode='w') as f:
        json.dump(account, f)


class User:
    def __init__(self, uid=0):
        self.uid = uid
        resp = connectApi(apiUrl=urls.getUserFullInfo.format(uid))
        info = resp.json()
        logging.debug(str(info))
        self.isExist = False
        self.isLogin = False
        if info['retcode'] == 0:
            self.info = info['data']
            self.posts = list()
            if uid == 0:
                self.isLogin = True
            self.isExist = True
        else:
            self.info = dict()
            self.posts = list()

    def getUid(self):
        return int(self.info['user_info']['uid']) if self.isExist else 0

    def getNickname(self):
        if self.uid == 0:
            return self.info['user_info']['nickname'] if self.isLogin else '未登录'
        else:
            return self.info['user_info']['nickname'] if self.isExist else '用户不存在'

    def getAvatar(self):
        return self.info['user_info'][
            'avatar_url'] if self.isExist else urls.defaultAvatar

    def getUserPost(self, offset=0, size=20):
        resp = connectApi(urls.userPost.format(offset, size, self.getUid()))
        posts = resp.json()['data']
        userPosts = dict(isLast=posts['is_last'], posts=articleSet(posts['list']), next=posts['next_offset'])

        return userPosts


class Actions:
    def follow(self, uid):
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.follow, method='post', headers=header, data={'entity_id': str(uid)}).json()
        logging.info(resp)
        return resp['retcode'], resp['message']

    def unfollow(self, uid):
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.follow, method='post', headers=header, data={'entity_id': str(uid)}).json()
        logging.info(resp)
        return resp['retcode'], resp['message']

    def upvotePost(self, post_id, isCancel):
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.upvotePost, method='post', headers=header, data={"post_id": post_id, "is_cancel": isCancel}).json()
        logging.info(resp)
        return resp['retcode'], resp['message']

    def collectPost(self, post_id, isCancel):
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.collectPost, method='post', headers=header, data={"post_id": post_id, "is_cancel": isCancel}).json()
        logging.info(resp)
        return resp['retcode'], resp['message']

    def getHistory(self, offset=''):
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.history.format(str(offset)), headers=header).json()['data']
        return articleSet(resp['list'], method='history'), resp['is_last']

    def releaseReply(self, delta, text, post_id, reply_id=''):
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        delta = json.dumps(delta['ops'], ensure_ascii=False)
        reply_contents = {
            "content": text,
            "post_id": str(post_id),
            "reply_id": str(reply_id),
            "structured_content": delta
        }
        resp = connectApi(urls.releaseReply, method='post', data=reply_contents, headers=header).json()
        return resp['retcode'], resp['message']



def debug(path='./debugs/'):
    url = urls.collectPost
    body = {"is_cancel": False, "post_id": "42109377"}
    header = headerGenerate()
    pprint.pprint(header)
    resp = connectApi(apiUrl=url, method='post', data=body, headers=header)
    contents = resp.text
    savedAt = f'{path}/debug-{int(time.time())}.json'
    with open(savedAt, mode='w') as f:
        f.write(contents)
    print(f"\nthe result was saved at {os.path.abspath(savedAt)} , here are previews\n")
    pprint.pprint(contents)
