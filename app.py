# encoding:utf-8
import os
import signal
import sys
import time
import platform
import logging
from functools import wraps
from tkinter import Tk, messagebox
import ctypes

import jinja2
from flask import Flask, render_template, request, redirect, make_response, send_file, url_for, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import libhoyolab
import webview

from libhoyolab import accountLogin

appicon_dir = './resources/appicon.ico'
config_dir = './configs/config.json'
logs_dir = './logs'

if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)

logging.basicConfig(filename=f"{logs_dir}/app-{int(time.time())}.log",
                    filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)

root = Tk()
root.withdraw()
ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
root.tk.call('tk', 'scaling', ScaleFactor / 75)

configLoadFailed = False
try:
    with open(config_dir) as f:
        config = json.load(f)
except:
    config = {"openLoad": "ys", "enableDebug": "off"}
    configLoadFailed = True
    logging.warning('configs load failed')
    messagebox.showwarning(title="配置文件加载失败",
                           message=f"尝试加载配置文件时出现错误，因此您的所有设置将无法被保存！")

if not (os.path.exists('./resources')):
    logging.error('resource load failed')
    messagebox.showerror(title="资源文件加载失败", message=f"尝试加载资源文件时出现错误！")
    sys.exit(-1)

openLoad = nowPage = config['openLoad']
debug = True if config['enableDebug'] == 'on' else False
logging.info(f"debug mode: {config['enableDebug']}")
theme = 'standard'
if 'theme' in config:
    theme = config['theme']
if not (os.path.exists(f'./theme/{theme}/templates') and os.path.exists(f'./theme/{theme}/static')):
    logging.error('gui load failed')
    messagebox.showerror(title="用户界面加载失败", message=f"尝试加载 {theme} 时出现错误！")
    sys.exit(-1)

games = dict(bh3='1', ys='2', bh2='3', wd='4', dby='5', sr='6', zzz='8')
gamesById = ['bh3', 'ys', 'bh2', 'wd', 'dby', 'sr', '', 'zzz']
gamesName = {'bh3': '崩坏3', 'ys': '原神', 'bh2': '崩坏学园2', 'wd': '未定事件簿', 'dby': '大别野',
             'sr': '崩坏：星穹铁道', '': '空', 'zzz': '绝区零'}
token = webview.token
appUserAgent = f'HoMoLab/114.514 (token-{token})'
firstAccess = True

account = libhoyolab.Account()

app = Flask(__name__, template_folder=f'./theme/{theme}/templates', static_folder=f'./theme/{theme}/static')
app.wsgi_app = ProxyFix(app.wsgi_app)


def LoadPage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global firstAccess, nowPage
        logging.info("=" * 15)
        logging.info(f"access url: {request.url}")
        logging.info(f"remote ip: {request.remote_addr}")
        logging.info(f"user agent: {request.user_agent.string}")
        userAgent = request.user_agent.string
        if userAgent != appUserAgent and ((request.cookies['token'] != token) or firstAccess):
            logging.info('browser that not allowed')
            return "<h1>app鉴权失败！</h1>", 403
        else:
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
                    window.set_title("错误")
                    return f'<h1 style="color: red;margin: 0 auto">尝试加载 {e} 时出现错误！</h1>'
                except Exception as e:
                    logging.info(f"Error! {e}")
                    return render_template('error.html'), 500

    return wrapper


@app.route('/favicon.ico')
def favicon():
    return send_file(appicon_dir)


# 文章页
@app.route('/article')
@LoadPage
def article():
    post_id = request.args.get("id")
    thread = libhoyolab.Article(post_id=post_id)
    render_method = thread.getRenderType()
    game = gamesById[int(thread.getGameId()) - 1]
    return render_template('article.html', thread=thread, type=render_method, game=game, account=account)


# 文章评论
@app.route('/comments')
@LoadPage
def comments():
    post_id = request.args.get("id")
    gid = request.args.get("gid")
    page = request.args.get("page") if 'page' in request.args else '1'
    replies = libhoyolab.Comments(post_id=post_id, gid=gid, page=page)
    return render_template('comment.html', thread=replies, account=account)


# 游戏分区主页
@app.route('/<game>')
@LoadPage
def main(game):
    global nowPage
    nowPage = game
    page = int('1' if 'page' not in request.args else request.args.get('page'))
    logging.info(page)
    return render_template('main.html',
                           articles=libhoyolab.Page(gid=games[game], page=page, pageType='recommend').getArticles(),
                           select='recommend', game=game, page=page, isLast=False, account=account)


# 搜索
@app.route('/<game>/search')
@LoadPage
def search(game):
    content = request.args.get('content')
    gameid = games[game]
    page = int('1' if 'page' not in request.args else request.args.get('page'))
    search_result = libhoyolab.Search(keyWords=content, gid=gameid, page=page)
    return render_template('main.html', articles=search_result.getArticles(), search=content,
                           select='search', game=game, page=page, isLast=search_result.isLastFlag, account=account)


# 官方资讯
@app.route('/<game>/news')
@LoadPage
def news(game):
    global nowPage
    nowPage = game
    requestType = request.args.get('type') if 'type' in request.args else 'announce'
    page = int(request.args.get('page') if 'page' in request.args else '1')
    return render_template('main.html',
                           articles=libhoyolab.Page(gid=games[game], page=page, pageType=requestType).getArticles(),
                           select=requestType, game=game, page=page, account=account)


@app.route('/setting', methods=['POST', 'GET'])
@LoadPage
def setting():
    global config, nowPage, openLoad
    if request.method == 'GET':
        return render_template('settings.html',
                               game=nowPage,
                               isSaved=False,
                               configLoadFailed=configLoadFailed,
                               config=config, account=account)
    else:
        logging.info("the new settings had been uploaded!")
        settings = request.form.to_dict()
        for k in settings:
            config[k] = settings[k]
        openLoad = config['openLoad']
        nowPage = openLoad
        window.set_title(f'米游社 - {gamesName[openLoad]}')
        if not configLoadFailed:
            with open('configs/config.json', mode='w+') as fp:
                json.dump(config, fp)
                logging.info(fp.read())
        return render_template('settings.html',
                               game=nowPage,
                               isSaved=True if not configLoadFailed else False,
                               configLoadFailed=configLoadFailed,
                               config=config, account=account)


# 跳转到原神分区
@app.route('/')
@LoadPage
def index():
    window.set_title(f'米游社 - {gamesName[openLoad]}')
    return redirect(f'/{openLoad}')


class Apis:
    def accountHandler(self):
        global account
        logging.info("="*15)
        logging.debug("accountHandler")
        if account.isLogging:
            if window.create_confirmation_dialog("登录", "确定退出登录吗？"):
                libhoyolab.logout()
                account = libhoyolab.Account()
        else:
            accountLogin.login()
            if window.create_confirmation_dialog("登录", "若以完成登录，请点击确定按钮"):
                libhoyolab.login()
                account = libhoyolab.Account()
        return {'status': 'ok'}


if __name__ == '__main__':
    apis = Apis()
    if platform.system() == 'Windows':
        try:
            window = webview.create_window('米游社', app, min_size=(650, 800), width=1280, height=1000, js_api=apis)
            webview.start(gui="edgechromium", user_agent=appUserAgent, debug=debug)

        except KeyError:
            pass

        except KeyboardInterrupt:
            pass

        except:
            messagebox.showerror(title="运行环境错误", message="请检查当前系统环境是否支持 EdgeWebview2")

    else:
        messagebox.showerror(title="运行环境错误", message="当前应用仅支持在Windows环境下运行")
