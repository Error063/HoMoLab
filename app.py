# encoding:utf-8
import os
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
import libhoyolab
import webview

from libhoyolab import accountLogin

if platform.system() == 'Windows':
    import winreg

init_time = str(int(time.time()))

appicon_dir = './resources/appicon.ico'
config_dir = './configs/config.json'
logs_dir = './logs'
gamesName = {'bh3': ['崩坏3', '1'], 'ys': ['原神', '2'], 'bh2': ['崩坏学园2', '3'], 'wd': ['未定事件簿', '4'], 'dby': ['大别野', '5'],
             'sr': ['崩坏：星穹铁道', '6'], 'none': ['空', '-1'], 'zzz': ['绝区零', '8']}
actions = {"article": "文章", "recommend": "推荐", "announce": "公告", "activity": "活动", "information": "资讯",
           "history": "历史", "search": "搜索", "setting": "设置", "user": "用户", "error": "错误"}
localization = {'global.quitConfirmation': '确定关闭?'}

if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)

logging.basicConfig(filename=f"{logs_dir}/app-{init_time}.log",
                    filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)

try:
    with open(config_dir) as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"openLoad": "ys", "enableDebug": "off", "colorFollowSystem": "on", "colorMode": "auto", "theme": "default"}
    logging.warning('configs load failed, creating...')
    if not os.path.exists(config_dir + '/..'):
        os.mkdir(config_dir + '/..')
    with open(config_dir, mode='w') as f:
        json.dump(config, f)

root = Tk()
root.withdraw()
ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
root.tk.call('tk', 'scaling', ScaleFactor / 75)

if not (os.path.exists('./resources')):
    logging.error('resource load failed')
    messagebox.showerror(title="资源文件加载失败", message=f"尝试加载资源文件时出现错误！")
    sys.exit(-1)

openLoad = nowPage = config['openLoad']
debug = True if config['enableDebug'] == 'on' else False
logging.info(f"debug mode: {config['enableDebug']}")
theme = 'default'
if 'theme' in config:
    theme = config['theme']
if not (os.path.exists(f'./theme/{theme}/templates') and os.path.exists(f'./theme/{theme}/static')):
    logging.error(f'load custom theme {theme} failed')
    theme = 'default'
    messagebox.showwarning(title="用户界面加载失败", message=f"尝试加载 {theme} 时出现错误！已切换到默认主题。")
    if not (os.path.exists(f'./theme/{theme}/templates') and os.path.exists(f'./theme/{theme}/static')):
        logging.error('gui load failed')
        messagebox.showerror(title="用户界面加载失败", message=f"尝试加载 {theme} 时出现错误！")
        sys.exit(-1)

token = webview.token
appUserAgent = f'HoMoLab/114.514 (token-{token})'
firstAccess = True
account = libhoyolab.User()

app = Flask(__name__, template_folder=f'./theme/{theme}/templates', static_folder=f'./theme/{theme}/static')


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


# def LoadPage(*args, **kwargs):
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
            account = libhoyolab.User()
            if debug:
                resp = make_response(func(*args, **kwargs))
                resp.set_cookie('token', token)
                if firstAccess:
                    firstAccess = False
                return resp
            else:
                try:
                    resp = make_response(func(*args, **kwargs))
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
                    return render_template('error.html', select='error', viewActions=actions), 500
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
            with open(f'./theme/{theme}/static/css/darkmode.css') as f:
                css += f.read()
        except FileNotFoundError:
            css += ''
        if config['colorMode'] == 'auto':
            css += '\n}'
    resp = make_response(css)
    resp.content_type = "text/css"
    return resp


@app.route('/resources')
def resources():
    """
    返回应用资源
    :return:
    """
    if 'logo' in request.args:
        logo = request.args.get('logo')
        if logo in gamesName.keys():
            return send_file(f'./resources/logos/{logo}.jpg')
        if logo == 'appicon':
            return send_file(f'./resources/logos/appicon.png')
        else:
            return '404 File not Found!', 404
    elif 'js' in request.args:
        return send_file('./resources/js/main.js')
    elif 'css' in request.args:
        match request.args.get('css'):
            case 'hoyolab':
                return send_file('./resources/css/hoyolabstyles.css')
            case _:
                return '404 File not Found!', 404
    elif 'font' in request.args:
        match request.args.get('font'):
            case '34ec64a':
                return send_file('./resources/font/iconfont.34ec64a.woff')
            case '33542c4':
                return send_file('./resources/font/iconfont.33542c4.ttf')
            case '72957bf':
                return send_file('./resources/font/iconfont.72957bf.woff2')
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
    # game = gamesById[int(thread.result["data"]['post']['post']['game_id']) - 1]
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
        return render_template('subcomment.html', prev_id=prev_id, floor_id=floor_id, reply_id=reply_id, replies=subReplies, rootReply=rootReply, account=account)
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
    window.set_title(f'HoMoLab - {gamesName[game][0]}')
    page = int('1' if 'page' not in request.args else request.args.get('page'))
    logging.info(page)
    return render_template('posts.html',
                           articles=libhoyolab.Page(gid=gamesName[game][1], page=page, pageType='recommend').articles,
                           select='recommend', game=nowPage, viewActions=actions, page=page, isLast=False, account=account)


# 搜索
@app.route('/<game>/search')
@LoadPage
def search(game):
    """
    在游戏分区中搜索文章
    :param game: 游戏简称（例如ys -> 原神，相应简称可在上方字典gamesName找到）
    :return:
    """
    keyword = request.args.get('keyword')
    gameid = gamesName[game][1]
    page = int('1' if 'page' not in request.args else request.args.get('page'))
    search_result = libhoyolab.Search(keyWords=keyword, gid=gameid, page=page)
    return render_template('posts.html', articles=search_result.articles, search=keyword,
                           select='search', game=nowPage, viewActions=actions, page=page, isLast=search_result.isLastFlag, account=account)


# 官方资讯
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
                           articles=libhoyolab.Page(gid=gamesName[game][1], page=page, pageType=requestType).articles,
                           select=requestType, game=nowPage, viewActions=actions, page=page, account=account)


@app.route('/setting', methods=['POST', 'GET'])
@LoadPage
def setting():
    """
    设置
    :return:
    """
    global config, nowPage, openLoad
    if request.method == 'GET':
        return render_template('settings.html', select='setting', game=nowPage, viewActions=actions, isSaved=False, config=config,
                               account=account)
    else:
        logging.info("the new settings had been uploaded!")
        settings = request.form.to_dict()
        for k in settings:
            config[k] = settings[k]
        openLoad = config['openLoad']
        with open('configs/config.json', mode='w+') as fp:
            json.dump(config, fp)
            logging.info(fp.read())
        return render_template('settings.html', select='setting', game=nowPage, viewActions=actions, isSaved=True, config=config,
                               account=account)


@app.route('/user')
@LoadPage
def user():
    """
    用户页
    :return:
    """
    uid = request.args.get('uid') if 'uid' in request.args else 0
    userInfos = libhoyolab.User(int(uid))
    return render_template('user.html', select='user', account=account, game=nowPage, viewActions=actions, user=userInfos,)


@app.route('/history')
def history():
    """
    浏览历史
    :return:
    """
    page = int(request.args.get('page')) if 'page' in request.args else 1
    offset = ((page - 1) * 20) + 1
    history_posts = libhoyolab.Actions().getHistory(offset)
    return render_template('posts.html', articles=history_posts[0], select='history', game=nowPage,
                           page=page, account=account, isLast=history_posts[1], viewActions=actions)


# 跳转到指定分区
@app.route('/')
@LoadPage
def index():
    """
    应用主页
    :return:
    """
    window.set_title(f'HoMoLab - {gamesName[nowPage][0]}')
    return redirect(f'/{nowPage}')


class Apis:
    def accountHandler(self):
        global account
        logging.info("=" * 15)
        logging.debug("accountHandler")
        if account.isLogin:
            if window.create_confirmation_dialog("登录", "确定要退出登录吗？"):
                logging.info(f'{account.getNickname()} had been logoff')
                libhoyolab.logout()
                account = libhoyolab.User()
        else:
            accountLogin.login()
            if window.create_confirmation_dialog("登录", "若已在弹出的窗口中完成登录，请点击确定按钮"):
                libhoyolab.login()
                account = libhoyolab.User()
                logging.info(f'login by {account.getNickname()}')
        return {'status': 'ok'}

    def refreshLoginStatus(self):
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
        result = libhoyolab.Actions.releaseReply(delta, text, post_id, reply_id)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            print(result)
            return {'status': f'{result[-1]}'}

    def getColor(self):
        logging.info("=" * 15)
        logging.debug("getColor")
        return {"colorSet": systemColorSet()}

    def followUser(self, uid, action):
        if action == 'unfollow':
            result = libhoyolab.Actions.follow(uid)
        else:
            result = libhoyolab.Actions.unfollow(uid)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    def upVote(self, post_id, isCancel):
        result = libhoyolab.Actions.upvotePost(post_id, isCancel)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    def upVoteReply(self, reply_id, post_id, isCancel):
        result = libhoyolab.Actions.upvoteReply(reply_id, post_id, isCancel)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    def collectPost(self, post_id, isCancel):
        result = libhoyolab.Actions.collectPost(post_id, isCancel)
        if result[0] == 0:
            return {'status': 'ok'}
        else:
            return {'status': f'err, {result[-1]}'}

    def maxWindow(self):
        window.toggle_fullscreen()
        return {'status': 'ok'}


if __name__ == '__main__':
    apis = Apis()
    if platform.system() == 'Windows':
        try:
            window = webview.create_window('HoMoLab', app, min_size=(1280, 800), width=1280, height=1000, js_api=apis,
                                           focus=True)
            webview.start(gui="edgechromium", user_agent=appUserAgent, debug=debug, localization=localization)
        except KeyError:
            pass
        except KeyboardInterrupt:
            pass
        except webview.util.WebViewException:
            messagebox.showerror(title="运行环境错误", message="请检查当前系统环境是否支持 EdgeWebview2")
    else:
        messagebox.showerror(title="运行环境错误", message="当前应用仅支持在Windows环境下运行")
