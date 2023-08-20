"""
应用主文件
(C) 2023 - forever Error063
Licensed under GPL 3 license
"""
import os
import pathlib
import sys
import time
import platform
import logging
from functools import wraps
from tkinter import Tk, messagebox
import ctypes

import jinja2
from flask import Flask, render_template, request, redirect, make_response, send_file
import json
import webview

from homo.libhoyolab import libhoyolab, accountLogin

if platform.system() == 'Windows':
    import winreg

init_time = str(int(time.time()))

version = '0.9.5.3'
home_dir = str(pathlib.Path.home())
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
run_dir = os.path.join(home_dir, 'homolab-dir')
appicon_dir = os.path.join(app_dir, 'resources', 'appicon.ico')
resources_dir = os.path.join(app_dir, 'resources')
config_dir = os.path.join(run_dir, 'configs')
config_file = os.path.join(config_dir, 'config.json')
logs_dir = os.path.join(run_dir, 'logs')
gameDict = {'bh3': ['崩坏3', '1'], 'ys': ['原神', '2'], 'bh2': ['崩坏学园2', '3'], 'wd': ['未定事件簿', '4'],
            'dby': ['大别野', '5'],
            'sr': ['崩坏：星穹铁道', '6'], 'none': ['空', '-1'], 'zzz': ['绝区零', '8']}
actions = {"article": "文章", "recommend": "推荐", "announce": "公告", "activity": "活动", "information": "资讯",
           "history": "历史", "search": "搜索", "setting": "设置", "user": "用户", "error": "错误", "login": "登录"}
localization = {'global.quitConfirmation': '确定关闭?'}


if not os.path.exists(run_dir):
    os.mkdir(run_dir)

if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)

logging.basicConfig(filename=os.path.join(logs_dir, f"app-{init_time}.log"),
                    filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
config = {"openLoad": "ys", "enableDebug": "off", "colorFollowSystem": "on", "colorMode": "auto",
          "theme": "default", "usingSystemWallpaper": "off"}

try:
    with open(config_file) as f:
        config_read = json.load(f)
    for c in config_read:
        config[c] = config_read[c]
    with open(config_file, mode='w') as f:
        json.dump(config, f)
except FileNotFoundError:
    logging.warning('configs load failed, creating...')
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)
    with open(config_file, mode='w') as f:
        json.dump(config, f)

root = Tk()
root.withdraw()
if platform.system() == 'Windows':
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    root.tk.call('tk', 'scaling', ScaleFactor / 75)

if not (os.path.exists(resources_dir)):
    logging.error('resource load failed')
    messagebox.showerror(title="资源文件加载失败", message=f"尝试加载资源文件时出现错误！")
    sys.exit(-1)

openLoad = nowPage = config['openLoad']
logging.info(f"debug mode: {config['enableDebug']}")
theme = 'default'
if 'theme' in config:
    theme = config['theme']
if not (os.path.exists(os.path.join(app_dir, 'theme', theme, 'templates')) and os.path.exists(
        os.path.join(app_dir, 'theme', theme, 'static'))):
    logging.error(f'load custom theme {theme} failed')
    theme = 'default'
    messagebox.showwarning(title="用户界面加载失败", message=f"尝试加载 {theme} 时出现错误！已切换到默认主题。")
    if not (os.path.exists(os.path.join(app_dir, 'theme', theme, 'templates')) and os.path.exists(
            os.path.join(app_dir, 'theme', theme, 'static'))):
        logging.error('gui load failed')
        messagebox.showerror(title="用户界面加载失败", message=f"尝试加载 {theme} 时出现错误！")
        sys.exit(-1)

window: webview.Window = None
token = webview.token
appUserAgent = f'HoMoLab/114.514 (token-{token})'
firstAccess = True
load = True

app = Flask(__name__, template_folder=os.path.join(app_dir, 'theme', theme, 'templates'),
            static_folder=os.path.join(app_dir, 'theme', theme, 'static'))


def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


app.after_request(after_request)


def systemColorSet():
    """
    从注册表中获取系统颜色
    :return:
    """
    if config['colorFollowSystem'] == 'on' and platform.system() == 'Windows':
        if winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\DWM"),
                               'ColorPrevalence')[0] == 1:
            color = hex(winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\DWM"),
                                            'ColorizationColor')[0])[4:]
        else:
            color = 'ffffff'
        light = winreg.QueryValueEx(
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"),
            'AppsUseLightTheme')[0]
    else:
        color = '66adff'
        light = 1
    return color, light


def getWallpaper():
    """
    获取用户壁纸
    :return:
    """
    if config['usingSystemWallpaper'] == 'on' and platform.system() == 'Windows':
        # return winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop"), 'WallPaper')[0]
        return os.path.expanduser('~') + r'\AppData\Roaming\Microsoft\Windows\Themes\TranscodedWallpaper'
    elif config['usingSystemWallpaper'] == 'on' and platform.system() == 'Linux':
        return 'image-api'
    else:
        return os.path.join(resources_dir, 'default.png')


def LoadPage(func):
    """
    请求执行前的处理（应用鉴权，异常捕获）
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        global firstAccess, nowPage, account
        logging.info("=" * 15)
        logging.info(f"access url: {request.url}")
        logging.info(f"remote ip: {request.remote_addr}")
        logging.info(f"user agent: {request.user_agent.string}")
        userAgent = request.user_agent.string
        if userAgent != appUserAgent:
            logging.info('browser that not allowed')
            return '<h1 style="color: red;text-align: center">APP鉴权失败！</h1>', 403
        else:
            if config['enableDebug'] == 'on':
                account = libhoyolab.User()
                page = func(*args, **kwargs)
                resp = make_response(page)
                resp.set_cookie('token', token)
                if firstAccess:
                    firstAccess = False
                return resp
            else:
                try:
                    account = libhoyolab.User()
                    page = func(*args, **kwargs)
                    resp = make_response(page)
                    resp.set_cookie('token', token)
                    if firstAccess:
                        firstAccess = False
                    return resp
                except jinja2.exceptions.TemplateNotFound as e:
                    logging.error(os.getcwd())
                    window.set_title("错误")
                    return f'<h1 style="color: red;text-align: center">尝试加载 {e} 时出现错误！</h1>'
                except Exception as e:
                    logging.info(f"Error! {e}")
                    return render_template('error.html', select='error', viewActions=actions, account=account), 500

    return wrapper


@app.route('/favicon.ico')
def favicon():
    """
    网页图标
    :return:
    """
    return send_file(appicon_dir)


@app.route('/personal.css')
def personal():
    """
    个性化颜色
    :return:
    """
    colorSet = systemColorSet()
    css = """.headers { 
    background-color: #""" + colorSet[0] + """;
}
"""
    if (not bool(colorSet[1]) and config['colorMode'] == 'auto') or config['colorMode'] == 'dark':
        if config['colorMode'] == 'auto':
            css += '@media (prefers-color-scheme: dark) {\n'
        try:
            with open(os.path.join(app_dir, 'theme', theme, 'static', 'css', 'darkmode.css')) as f:
                css += f.read()
        except FileNotFoundError:
            css += ''
        if config['colorMode'] == 'auto':
            css += '\n}'
    resp = make_response(css)
    resp.content_type = "text/css"
    return resp


@app.route('/wallpaper')
def wallpaper():
    """
    返回壁纸
    :return:
    """
    wallpaper_path = getWallpaper()
    try:
        if wallpaper_path != 'image-api':
            return send_file(wallpaper_path)
        else:
            return redirect("https://t.mwm.moe/pc/")
    except FileNotFoundError:
        # return send_file('./resources/default.png')
        return redirect("https://t.mwm.moe/pc/")


@app.route('/resources')
def resources():
    """
    返回应用资源
    :return:
    """
    if 'logo' in request.args:
        logo = request.args.get('logo')
        if logo in gameDict.keys():
            return send_file(os.path.join(resources_dir, 'logos', f'{logo}.jpg'))
        if logo == 'appicon':
            return send_file(os.path.join(resources_dir, 'logos', 'appicon.png'))
        else:
            return '404 File not Found!', 404
    elif 'js' in request.args:
        return send_file(os.path.join(resources_dir, 'js', 'main.js'))
    elif 'css' in request.args:
        match request.args.get('css'):
            case 'hoyolab':
                return send_file(os.path.join(resources_dir, 'css', 'hoyolabstyles.css'))
            case _:
                return '404 File not Found!', 404
    elif 'font' in request.args:
        match request.args.get('font'):
            case '34ec64a':
                return send_file(os.path.join(resources_dir, 'font', 'iconfont.34ec64a.woff'))
            case '33542c4':
                return send_file(os.path.join(resources_dir, 'font', 'iconfont.33542c4.ttf'))
            case '72957bf':
                return send_file(os.path.join(resources_dir, 'font', 'iconfont.72957bf.woff2'))
            case _:
                return '404 File not Found!', 404
    else:
        return '404 File not Found!', 404


@app.route('/article')
@LoadPage
def article():
    """
    文章页
    :return:
    """
    post_id = request.args.get("id")
    thread = libhoyolab.Article(post_id=post_id)
    render_method = thread.result["data"]['post']['post']['view_type']
    return render_template('article.html', select='article', thread=thread, type=render_method, game=nowPage,
                           account=account, viewActions=actions)


@app.route('/comments')
@LoadPage
def comments():
    """
    文章评论
    :return:
    """
    post_id = request.args.get("id")
    gid = request.args.get("gid")
    if 'reply_id' in request.args and 'floor_id' in request.args:
        reply_id = request.args.get('reply_id')
        floor_id = request.args.get('floor_id')
        last_id = request.args.get("last_id") if 'last_id' in request.args else '0'
        prev_id = request.args.get("prev_id") if 'prev_id' in request.args else '-1'
        rootReply = libhoyolab.RootComment(post_id, reply_id)
        subReplies = libhoyolab.SubComments(post_id, floor_id, last_id, gid)
        return render_template('subcomment.html', prev_id=prev_id, floor_id=floor_id, reply_id=reply_id,
                               replies=subReplies, rootReply=rootReply, account=account)
    else:
        page = request.args.get("page") if 'page' in request.args else '1'
        replies = libhoyolab.Comments(post_id=post_id, gid=gid, page=page)
        return render_template('comment.html', replies=replies, account=account)


@app.route('/<game>')
@LoadPage
def main(game):
    """
    游戏分区主页
    :param game: 游戏简称（例如ys -> 原神，相应简称可在上方字典gamesName找到）
    :return:
    """
    global nowPage
    nowPage = game
    window.set_title(f'HoMoLab - {gameDict[game][0]}')
    page = int('1' if 'page' not in request.args else request.args.get('page'))
    logging.info(page)
    return render_template('posts.html',
                           articles=libhoyolab.Page(gid=gameDict[game][1], page=page, pageType='recommend').articles,
                           select='recommend', game=nowPage, viewActions=actions, page=page, isLast=False,
                           account=account)


@app.route('/<game>/forum')
def forum(game):
    pass


@app.route('/<game>/search')
@LoadPage
def search(game):
    """
    在游戏分区中搜索文章
    :param game: 游戏简称（例如ys -> 原神，相应简称可在上方字典gamesName找到）
    :return:
    """
    keyword = request.args.get('keyword')
    gameid = gameDict[game][1]
    page = int('1' if 'page' not in request.args else request.args.get('page'))
    search_result = libhoyolab.Search(keyWords=keyword, gid=gameid, page=page)
    return render_template('posts.html', articles=search_result.articles, search=keyword, select='search', game=nowPage,
                           viewActions=actions, page=page, isLast=search_result.isLastFlag, account=account)


@app.route('/<game>/news')
@LoadPage
def news(game):
    """
    获取游戏官方资讯
    :param game: 游戏简称（例如 ys -> 原神，相应简称可在上方字典gamesName找到）
    :return:
    """
    global nowPage
    nowPage = game
    requestType = request.args.get('type') if 'type' in request.args else 'announce'
    page = int(request.args.get('page') if 'page' in request.args else '1')
    return render_template('posts.html',
                           articles=libhoyolab.Page(gid=gameDict[game][1], page=page, pageType=requestType).articles,
                           select=requestType, game=nowPage, viewActions=actions, page=page, account=account)


@app.route('/setting', methods=['POST', 'GET'])
@LoadPage
def setting():
    """
    设置
    :return:
    """
    global config, nowPage, openLoad, load
    if request.method == 'GET':
        return render_template('settings.html', select='setting', game=nowPage, viewActions=actions, isSaved=False,
                               config=config, account=account, version=version, platform=platform.system())
    else:
        logging.info("the new settings had been uploaded!")
        settings = request.form.to_dict()
        for k in settings:
            config[k] = settings[k]
        openLoad = config['openLoad']
        with open(config_file, mode='w+') as fp:
            json.dump(config, fp)
            logging.info(fp.read())
        load = True
        window.destroy()


@app.route('/login', methods=['POST', 'GET'])
def login():
    if not account.isLogin:
        if request.method == 'GET':
            return render_template('login.html', select='login', game=nowPage, viewActions=actions, config=config,
                                   account=account, platform=platform.system())
        else:
            mysAccount = request.form.get('account')
            mysPassword = request.form.get('password')
            libhoyolab.login(methods='pwd', mysAccount=mysAccount, mysPasswd=mysPassword)
            return redirect('/')
    else:
        return redirect('/')


@app.route('/user')
@LoadPage
def user():
    """
    用户页
    :return:
    """
    uid = request.args.get('uid') if 'uid' in request.args else 0
    userInfos = libhoyolab.User(int(uid))
    return render_template('user.html', select='user', account=account, game=nowPage, viewActions=actions,
                           user=userInfos)


@app.route('/history')
def history():
    """
    浏览历史
    :return:
    """
    page = int(request.args.get('page')) if 'page' in request.args else 1
    offset = ((page - 1) * 20) + 1
    history_posts = libhoyolab.Actions.getHistory(offset)
    return render_template('posts.html', articles=history_posts[0], select='history', game=nowPage,
                           page=page, account=account, isLast=history_posts[1], viewActions=actions)


@app.route('/')
@LoadPage
def index():
    """
    应用主页（应用进入时的入口）
    :return:
    """
    window.set_title(f'HoMoLab - {gameDict[nowPage][0]}')
    return redirect(f'/{nowPage}')


@app.route('/<game>/vote')
def vote(game):
    # /ys/vote?id=1666798681485819904&uid=271413785
    vote_id = request.args.get('id')
    return redirect(f"https://www.miyoushe.com/{game}/vote?id={vote_id}")


@app.errorhandler(500)
def errorPage(e):
    return render_template('error.html', select='error', viewActions=actions, account=account), 500


class Apis:
    """
    向Pywebview提供JavaScript API
    """

    def accountHandler(self):
        """
        执行账户登录/退出登录操作
        :return: 操作状态
        """
        global account
        logging.info("=" * 15)
        logging.debug("accountHandler")
        if account.isLogin:
            if window.create_confirmation_dialog("登录", "确定要退出登录吗？"):
                logging.info(f'{account.getNickname()} had been logoff')
                libhoyolab.logout()
                account = libhoyolab.User()
        else:
            accountLogin.loginByWeb()
            if window.create_confirmation_dialog("登录", "若已在弹出的窗口中完成登录，请点击确定按钮"):
                libhoyolab.login()
                account = libhoyolab.User()
                logging.info(f'login by {account.getNickname()}')
        return {'status': 'ok'}

    def refreshLoginStatus(self):
        """
        使用本地存储的login_ticket登录信息向服务器请求登录状态
        :return: 操作状态
        """
        global account
        logging.info("=" * 15)
        logging.debug("refreshLoginStatus")
        status = libhoyolab.login()
        account = libhoyolab.User()
        if status != 'ok' and not account.isLogin:
            logging.error('failed to refresh login status from server!')
            window.evaluate_js(r'alert("尝试向服务器更新登录信息失败!")')
        else:
            logging.info(f'the user {account.getNickname()} login status had been updated successfully')
        return {'status': 'ok'}

    def deleteLog(self):
        """
        删除本地日志（不删除当前运行的日志）
        :return: 操作状态
        """
        logging.info("=" * 15)
        logging.debug("deleteLog")
        log_list = os.listdir(logs_dir)
        try:
            for log in log_list:
                if log != f'app-{init_time}.log':
                    os.unlink(f'{logs_dir}/{log}')
            logging.info("the logs was deleted successfully (keep recent log only)")
            return {'status': 'ok'}
        except Exception as e:
            logging.error(f'failed to delete log because {e}')
            return {'status': 'failed'}

    def releaseReply(self, delta, text, post_id, reply_id=''):
        """
        发布评论
        :param delta: 结构化文本信息
        :param text: 文本信息
        :param post_id: 文章id
        :param reply_id: 评论id（如果是给评论发评论，则需要传递此项）
        :return: 操作状态
        """
        result = libhoyolab.Actions.releaseReply(delta, text, post_id, reply_id)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            print(result)
            return {'status': f'{result[-1]}'}

    def getColor(self):
        """
        获取系统配色（Windows可用）
        :return: 系统颜色
        """
        logging.info("=" * 15)
        logging.debug("getColor")
        return {"colorSet": systemColorSet()}

    def followUser(self, uid, action):
        """
        关注/取关用户
        :param uid: 用户uid
        :param action: 操作（follow或unfollow）
        :return: 操作状态
        """
        if action == 'unfollow':
            result = libhoyolab.Actions.follow(uid)
        else:
            result = libhoyolab.Actions.unfollow(uid)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    def upVote(self, post_id, isCancel):
        """
        文章点赞
        :param post_id: 文章id
        :param isCancel: 是否取消
        :return: 操作状态
        """
        result = libhoyolab.Actions.upvotePost(post_id, isCancel)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    def upVoteReply(self, reply_id, post_id, isCancel):
        """
        评论点赞
        :param reply_id: 评论id
        :param post_id: 文章id
        :param isCancel: 是否取消
        :return: 操作状态
        """
        result = libhoyolab.Actions.upvoteReply(reply_id, post_id, isCancel)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    def collectPost(self, post_id, isCancel):
        """
        收藏文章
        :param post_id: 文章id
        :param isCancel: 是否取消
        :return: 操作状态
        """
        result = libhoyolab.Actions.collectPost(post_id, isCancel)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    # def pageContents(self, type, gid, forum_id):

    def openAppConfig(self):
        os.startfile(run_dir)


def enter():
    global load, window
    apis = Apis()
    if platform.system() == 'Windows' or config['enableDebug'] == 'on':
        try:
            while load:
                window = webview.create_window('HoMoLab', app, min_size=(1280, 800), width=1280, height=1000,
                                               js_api=apis, focus=True)
                load = False
                if not config['enableDebug'] == 'on':
                    webview.start(gui="edgechromium", user_agent=appUserAgent, localization=localization)
                else:
                    webview.start(user_agent=appUserAgent, debug=config['enableDebug'] == 'on',
                                  localization=localization)
                del window
                if load:
                    time.sleep(1)
        except KeyError:
            pass
        except KeyboardInterrupt:
            pass
        except webview.util.WebViewException:
            if not config['enableDebug'] == 'on':
                messagebox.showerror(title="运行环境错误", message="请检查当前系统环境是否支持 EdgeWebview2")
                sys.exit(-1)
            else:
                messagebox.showerror(title="运行环境错误", message="尝试初始化GUI时出现错误（当前运行于调试模式）")
                sys.exit(-1)
    else:
        messagebox.showerror(title="运行环境错误",
                             message="对其他操作系统的支持尚处于测试阶段\n如需使用，请手动修改configs/config.json中的'enableDebug'的值修改为'on'")
        sys.exit(-1)


if __name__ == '__main__':
    enter()