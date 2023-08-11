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
import logging

from libhoyolab import threadRender, urls

logger = logging.getLogger('libhoyolab')

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

config_dir = './configs'
config_file = f'{config_dir}/config.json'
account_file = f'{config_dir}/account.json'

if not os.path.exists(config_dir):
    os.mkdir(config_dir)

if os.path.exists(account_file):
    with open(account_file) as f:
        account = json.load(f)
else:
    account = {"isLogin": False, "login_ticket": "", "stuid": "", "stoken": ""}
    with open(account_file, mode='w') as f:
        json.dump(account, f)

_USERAGENT = f'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/105.0.5195.79 Mobile Safari/537.36 miHoYoBBS/{mysVersion}'
login_ticket = account["login_ticket"]
stuid = account["stuid"]
stoken = account["stoken"]
cookie = f'login_ticket={login_ticket}'

newsType = {'announce': '1', 'activity': '2', 'information': '3'}
gamesById = ['bh3', 'ys', 'bh2', 'wd', 'dby', 'sr', '', 'zzz']

session = requests.session()


def md5(text) -> str:
    """
    md5加密
    :param text: 需要加密的文本
    :return:
    """
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


def randomStr(n) -> str:
    """
    生成指定位数的随机字符串
    :param n: 指定位数
    :return:
    """
    return (''.join(random.sample(string.digits + string.ascii_letters, n))).lower()


def DS1() -> str:
    """
    生成米游社DS1
    :return:
    """
    n = Salt_LK2
    i = str(int(time.time()))
    r = randomStr(6)
    c = md5(f"salt={n}&t={i}&r={r}")
    return "{},{},{}".format(i, r, c)


def DS2(query='', body='', salt='4x') -> str:
    '''
    生成米游社DS2
    :param query: 查询参数（当算法为Ds2，请求为get时使用）
    :param body: post内容（当算法为Ds2，请求为post时使用）
    :param salt: 指定算法所需的salt（当算法为Ds2时使用）
    :return: str
    '''
    salt = Salt_4X if salt.lower() == '4x' else Salt_6X
    new_body = dict()
    t = int(time.time())
    r = random.randint(100001, 200000)
    main = ''
    if body:
        if type(body) is str:
            body = json.loads(body)
            for key in sorted(json.loads(body)):
                new_body[key] = body[key]
            body = json.dumps(new_body)
        elif type(body) is dict:
            for key in sorted(body):
                new_body[key] = body[key]
            body = json.dumps(new_body)
            main = f"salt={salt}&t={t}&r={r}&b={body}"
    elif query:
        query = '&'.join(sorted(query.split('&')))
        main = f"salt={salt}&t={t}&r={r}&q={query}"
    else:
        main = f"salt={salt}&t={t}&r={r}"
    ds = md5(main)
    return f"{t},{r},{ds}"


def headerGenerate(app='web', client='4', withCookie=True, withDs=True, agro=1, query='', body: str | dict = '{}',
                   salt='4x', Referer="https://www.miyoushe.com/") -> dict:
    """
    生成请求头
    :param app: ‘app’ 或 ‘web’
    :param client: 1：iOS 2：Android 4：网页 5：其他
    :param withCookie: 是否携带cookie信息
    :param withDs: 是否包含Ds（已弃用）
    :param agro: Ds算法（Ds1或Ds2）
    :param query: 查询参数（当算法为Ds2，请求为get时使用）
    :param body: post内容（当算法为Ds2，请求为post时使用）
    :param salt: 指定算法所需的salt（当算法为Ds2时使用）
    :param Referer: 请求头的Referer字段
    :return: dict
    """
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


def getEmotions(gid: str | int = '2') -> dict:
    """
    获取表情包所对应的图片路径
    :param gid:
    :return: dict
    """
    logger.info('emotion lib is running')
    emotionDict = dict()
    req = session.get(urls.emoticon_set.format(str(gid)), verify=False)
    contents = json.loads(req.content.decode("utf8"))['data']['list']

    for emotionSet in contents:
        for emotion in emotionSet['list']:
            emotionDict[emotion['name']] = emotion['icon']

    return emotionDict


def articleSet(raw_articles: list, method: str = 'normal') -> list:
    """
    生成简化后的文章流
    :param raw_articles: 原来的文章流
    :param method: 文章流类型
    :return:
    """
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
    """
    api连接
    :param apiUrl: url地址
    :param method: 连接方式（get 或 post）
    :param data: post内容
    :param headers: 请求头
    :return:
    """
    if headers is None:
        headers = headerGenerate(app='web')
    if data is None:
        data = {}
    count = 3  # 尝试三次
    err = None
    resp = None
    while count != 0:
        try:
            match method.lower():
                case 'get':
                    resp = session.get(url=apiUrl, headers=headers, verify=False, timeout=5)
                case 'post':
                    resp = session.post(url=apiUrl, headers=headers, json=data, verify=False, timeout=5)
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


def login():
    """
    用户登录操作
    :return:
    """
    global cookie, login_ticket, stuid, stoken, account
    logger.info("=" * 20)
    logger.info("logining...")
    with open(account_file) as f:
        login_ticket = json.load(f)['login_ticket']
    resp = session.get(urls.Cookie_url.format(login_ticket))
    data = json.loads(resp.text.encode('utf-8'))
    if "成功" in data["data"]["msg"]:
        stuid = data["data"]["cookie_info"]["account_id"]
        resp = session.get(url=urls.Cookie_url2.format(login_ticket, stuid))  # 获取stoken
        data = json.loads(resp.text.encode('utf-8'))
        stoken = data["data"]["list"][0]["token"]
        account = {"isLogin": True, "login_ticket": login_ticket, "stuid": stuid, "stoken": stoken}
        with open(account_file, mode='w') as f:
            json.dump(account, f)
        logger.info(f'success')
        return 'ok'
    else:
        logger.error(f'failed, {data}')
        return 'failed'


def logout():
    """
    用户退出登录操作
    :return:
    """
    global account, cookie, login_ticket, stuid, stoken
    logger.info("=" * 20)
    logger.info("logoff...")
    os.unlink(account_file)
    cookie = ''
    login_ticket = ''
    stuid = ''
    stoken = ''
    account = {"isLogin": False, "login_ticket": "", "stuid": "", "stoken": ""}
    with open(account_file, mode='w') as f:
        json.dump(account, f)


class Article:
    """
    文章类：从服务器索取文章信息
    """

    def __init__(self, post_id):
        """
        初始化文章类
        :param post_id: 文章id
        """
        logger.info(f'getting article from {post_id}')
        logger.info('accessing ' + urls.getPostFull.format(str(post_id)))
        headers = headerGenerate(app='web')
        resp = connectApi(urls.getPostFull.format(str(post_id)), headers=headers)
        self.result = resp.json()

    def getContent(self) -> str:
        """
        获取文章内容(基于HTML)
        :return:
        """
        return threadRender.replaceAll(self.result["data"]['post']['post']['content'],
                                       emotionDict=getEmotions(gid=self.result["data"]['post']['post']['game_id']))

    def getStructuredContent(self) -> str:
        """
        获取结构化的文章内容（基于Quill的Delta）
        :return:
        """
        structured = self.result["data"]["post"]["post"]["structured_content"]
        return threadRender.replaceAllFromDelta(structured, emotionDict=getEmotions(
            gid=self.result["data"]['post']['post']['game_id']))

    def getVideo(self) -> str:
        """
        获取视频及其不同的清晰度
        :return:
        """
        return json.dumps(self.result["data"]["post"]["vod_list"])

    def getSelfAttitude(self) -> bool:
        """
        获取用户是否给文章点赞
        :return:
        """
        return bool(self.result['data']['post']['self_operation']['attitude'])

    def getSelfCollect(self) -> bool:
        """
        获取用户是否给文章收藏
        :return:
        """
        return bool(self.result['data']['post']['self_operation']['is_collected'])

    def getVotes(self) -> int:
        """
        获取文章的点赞数
        :return:
        """
        return int(self.result['data']['post']['stat']['like_num'])

    def getCollects(self) -> int:
        """
        获取文章的收藏数
        :return:
        """
        return int(self.result['data']['post']['stat']['bookmark_num'])

    def getAuthorDescribe(self) -> str:
        """
        获取作者简介
        :return:
        """
        return f"{self.result['data']['post']['user']['certification']['label'] if len(self.result['data']['post']['user']['certification']['label']) > 0 else self.result['data']['post']['user']['introduce']}"

    def getTags(self) -> list:
        """
        获取文章标签
        :return:
        """
        tags = list()
        for tag in self.result['data']['post']['topics']:
            tags.append({
                'name': tag['name'],
                'cover': tag['cover'],
                'id': tag['id']
            })
        return tags


class Page:
    """
    文章流类
    """

    def __init__(self, gid, pageType, page=1, pageSize=50):
        """
        初始化文章流类
        :param gid: 论坛板块id
        :param pageType: 文章流类型
        :param page: 页数
        :param pageSize: 单次获取的最大的文章数量
        """
        self.page = page
        logger.info('getting page')
        if pageType == 'recommend':
            apiUrl = urls.webHome.format(str(gid), str(page), str(pageSize))
        elif pageType == 'feeds':  # 获取发现页时有问题
            apiUrl = urls.feedPosts.format(str(gid), str(page))
        else:
            if pageType not in newsType:
                typeNum = '1'
            else:
                typeNum = newsType[pageType]
            apiUrl = urls.getNewsList.format(str(gid), str(typeNum), str(pageSize),
                                             str(abs((int(page) - 1) * int(pageSize))))
        logger.info('accessing ' + apiUrl)
        req = connectApi(apiUrl)
        result = req.json()
        self.articles = articleSet(result['data']['recommended_posts' if pageType == 'recommend' else 'list'])


class Comments:
    """
    评论流类
    """

    def __init__(self, post_id, gid, page=1, max_size=20, rank_by_hot=True, orderby=1, only_master=False):
        """
        初始化评论流类
        :param post_id: 文章id
        :param gid: 游戏id
        :param page: 页数
        :param max_size: 单次获取的最大的评论数量
        :param rank_by_hot: 是否按热度排序
        :param orderby: 排序方式（1.最早，2.最新）
        :param only_master: 仅楼主
        """
        self.page = int(page)
        self.post_id = post_id
        self.gid = str(gid)
        start = abs((int(page) - 1) * int(max_size))
        logger.info(f"getting comments from {post_id}, start from {start}")
        emotionDict = getEmotions(gid)
        apiUrl = urls.getPostReplies.format(str(gid), str(rank_by_hot).lower(), str(post_id), str(max_size),
                                            str(start), str(orderby), str(only_master).lower())
        logger.info("accessing " + apiUrl)
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(apiUrl, headers=header)
        result = resp.json()
        # pprint.pprint(result)
        self.rank_by_hot = rank_by_hot
        self.comments = []
        comments: list = [None] * (max_size + 1) if rank_by_hot else [None] * max_size
        self.have_top = False
        self.isLastFlag = result['data']['is_last']
        comments_raw = result['data']['list']
        for i in range(len(comments_raw)):
            reply = comments_raw[i]
            tmp = {
                'reply_id': reply['reply']['reply_id'],
                'floor_id': reply['reply']['floor_id'],
                'post_id': reply['reply']['post_id'],
                'content': threadRender.replaceAllFromDelta(reply['reply']['struct_content'], emotionDict),
                'username': reply['user']['nickname'],
                'uid': int(reply['user']['uid']),
                'avatar': reply['user']['avatar_url'],
                'describe': reply['user']['certification']['label'] if len(
                    reply['user']['certification']['label']) > 0 else reply['user']['introduce'],
                'like_num': reply['stat']['like_num'],
                'sub_num': int(reply['stat']['sub_num']),
                'upvoted': bool(reply['self_operation']['reply_vote_attitude']) and bool(
                    reply['self_operation']['attitude'])
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


class RootComment:
    """
    评论类
    """

    def __init__(self, post_id, reply_id):
        """
        初始化评论类
        :param post_id: 文章id
        :param reply_id: 评论id
        """
        self.post_id = post_id
        self.reply_id = reply_id
        logger.info(f"getting root comment {reply_id} in {post_id}")
        logger.info(f"accessing {urls.getRootReplyInfo.format(str(post_id), str(reply_id))}")
        resp = connectApi(urls.getRootReplyInfo.format(str(post_id), str(reply_id))).json()['data']
        emotionDict = getEmotions(resp['reply']['reply']['game_id'])
        self.comment = {
            'reply_id': resp['reply']['reply']['reply_id'],
            'floor_id': resp['reply']['reply']['floor_id'],
            'post_id': resp['reply']['reply']['post_id'],
            'content': threadRender.replaceAllFromDelta(resp['reply']['reply']['struct_content'], emotionDict),
            'username': resp['reply']['user']['nickname'],
            'uid': int(resp['reply']['user']['uid']),
            'avatar': resp['reply']['user']['avatar_url'],
            'describe': resp['reply']['user']['certification']['label'] if len(
                resp['reply']['user']['certification']['label']) > 0 else resp['reply']['user']['introduce'],
            'like_num': resp['reply']['stat']['like_num'],
            'upvoted': bool(resp['reply']['self_operation']['reply_vote_attitude']) and bool(
                resp['reply']['self_operation']['attitude'])
        }


class SubComments:
    """
    楼中楼类
    """

    def __init__(self, post_id, floor_id, last_id=0, gid=2, max_size=20):
        """
        初始化楼中楼类
        :param post_id: 文章id
        :param floor_id: 评论楼层id
        :param last_id: 最后的评论id
        :param gid: 游戏id（仅限获取表情图片）
        :param max_size: 单次获取的最大的评论数量
        """
        self.post_id = post_id
        self.floor_id = floor_id
        self.prev_id = last_id
        self.gid = gid
        logger.info(f"getting sub comments from {floor_id} in {post_id}, start from id {last_id}")
        emotionDict = getEmotions(gid)
        apiUrl = urls.getSubReplies.format(str(post_id), str(floor_id), str(last_id), str(max_size))
        logger.info(f'accessing {apiUrl}')
        header = headerGenerate()
        resp = connectApi(apiUrl=apiUrl, headers=header).json()
        self.comments = list()
        self.isLastFlag = resp['data']['is_last']
        self.last_id = resp['data']['last_id']
        comments_raw = resp['data']['list']
        for reply in comments_raw:
            self.comments.append({
                'reply_id': reply['reply']['reply_id'],
                'post_id': reply['reply']['post_id'],
                'content': threadRender.replaceAllFromDelta(reply['reply']['struct_content'], emotionDict),
                'username': reply['user']['nickname'],
                'uid': int(reply['user']['uid']),
                'avatar': reply['user']['avatar_url'],
                'describe': reply['user']['certification']['label'] if len(
                    reply['user']['certification']['label']) > 0 else reply['user']['introduce'],
                'like_num': reply['stat']['like_num'],
                'upvoted': bool(reply['self_operation']['reply_vote_attitude']) and bool(
                    reply['self_operation']['attitude'])
            })


class Search:
    """
    搜索类
    """

    def __init__(self, keyWords, gid, page=1, max_size=20):
        """
        初始化搜索类
        :param keyWords: 关键字
        :param gid: 游戏id
        :param page: 页数
        :param max_size: 单次获取的最大的文章数量
        """
        self.gid = gid
        start = int(page)
        logger.info(f'searching {keyWords}, from {start}')
        logger.info(f'accessing {urls.searchPosts.format(str(gid), str(keyWords), str(start), str(max_size))}')
        req = connectApi(apiUrl=urls.searchPosts.format(str(gid), str(keyWords), str(start), str(max_size)))
        result = req.json()
        self.isLastFlag = result['data']['is_last']
        self.articles = articleSet(result['data']['posts'])


class User:
    """
    用户类
    """

    def __init__(self, uid=0):
        """
        初始化用户类
        :param uid: 请求的用户uid（若uid为0，则指向已登录的用户）
        """
        self.uid = uid
        logger.info(f"getting user {uid}'s informations")
        logger.info(f"accessing {urls.getUserFullInfo.format(uid)}")
        resp = connectApi(apiUrl=urls.getUserFullInfo.format(uid))
        info = resp.json()
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
        """
        获取用户uid（若不存在则返回0）
        :return:
        """
        return int(self.info['user_info']['uid']) if self.isExist else 0

    def getNickname(self):
        """
        获取用户昵称
        :return:
        """
        if self.uid == 0:
            return self.info['user_info']['nickname'] if self.isLogin else '未登录'
        else:
            return self.info['user_info']['nickname'] if self.isExist else '用户不存在'

    def getAvatar(self):
        """
        获取用户头像
        :return:
        """
        return self.info['user_info']['avatar_url'] if self.isExist else urls.defaultAvatar

    def getUserPost(self, offset=0, size=20):
        """
        获取用户所发表的文章
        :param offset:
        :param size: 单次获取的最大的文章数量
        :return:
        """
        resp = connectApi(urls.userPost.format(offset, size, self.getUid()))
        posts = resp.json()['data']
        userPosts = dict(isLast=posts['is_last'], posts=articleSet(posts['list']), next=posts['next_offset'])
        return userPosts


class Actions:
    """
    操作类
    """

    @staticmethod
    def follow(uid):
        """
        关注用户
        :param uid: 用户uid
        :return:
        """
        logger.info(f"following user {uid}")
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.follow, method='post', headers=header, data={'entity_id': str(uid)}).json()
        logger.info(resp)
        return resp['retcode'], resp['message']

    @staticmethod
    def unfollow(uid):
        """
        取关用户
        :param uid: 用户uid
        :return:
        """
        logger.info(f"unfollowing user {uid}")
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.follow, method='post', headers=header, data={'entity_id': str(uid)}).json()
        logger.info(resp)
        return resp['retcode'], resp['message']

    @staticmethod
    def upvotePost(post_id, isCancel):
        """
        文章点赞操作
        :param post_id: 文章id
        :param isCancel: 是否取消点赞
        :return:
        """
        logger.info(f'{"canceling " if isCancel else ""}upvote the post {post_id}')
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.upvotePost, method='post', headers=header,
                          data={"post_id": post_id, "is_cancel": isCancel}).json()
        logger.info(resp)
        return resp['retcode'], resp['message']

    @staticmethod
    def upvoteReply(reply_id, post_id, isCancel):
        """
        评论点赞操作
        :param reply_id: 评论id
        :param post_id: 文章id
        :param isCancel: 是否取消点赞
        :return:
        """
        logger.info(f'{"canceling " if isCancel else ""}upvote the reply {reply_id} in {post_id}')
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.upvoteReply, method='post', headers=header,
                          data={"post_id": post_id, "reply_id": reply_id, "is_cancel": isCancel, "gids": '1'}).json()
        logger.info(resp)
        return resp['retcode'], resp['message']

    @staticmethod
    def collectPost(post_id, isCancel):
        """
        收藏文章
        :param post_id: 文章id
        :param isCancel: 是否取消收藏
        :return:
        """
        logger.info(f'{"canceling " if isCancel else ""}collect the post{post_id}')
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.collectPost, method='post', headers=header,
                          data={"post_id": post_id, "is_cancel": isCancel}).json()
        return resp['retcode'], resp['message']

    @staticmethod
    def getHistory(offset=''):
        """
        获取用户浏览历史
        :param offset:
        :return:
        """
        logger.info("getting user's history")
        header = headerGenerate(app='app', client='2', Referer='https://app.mihoyo.com')
        resp = connectApi(urls.history.format(str(offset)), headers=header).json()['data']
        return articleSet(resp['list'], method='history'), resp['is_last']

    @staticmethod
    def releaseReply(delta, text, post_id, reply_id=''):
        """
        发布评论
        :param delta: 评论的delta结构化信息（基于quill.js）
        :param text: 评论文本
        :param post_id: 发布到的文章uid
        :param reply_id: 回复楼中楼的id
        :return:
        """
        logger.info(f"releasing the reply to post {post_id} with content {text}")
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
    """
    api调试
    :param path:
    :return:
    """
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
