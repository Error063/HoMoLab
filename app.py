# encoding:utf-8
import os
import time
import platform
import logging
from functools import wraps
from tkinter import Tk, messagebox

from flask import Flask, render_template, request, redirect, make_response, send_file, url_for, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import libhoyolab
import webview

appicon_dir = './resources/appicon.ico'
config_dir = './configs/config.json'
logs_dir = './logs'

if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)

logging.basicConfig(filename=f"{logs_dir}/app-{int(time.time())}.log",
                    filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)

with open(config_dir) as f:
    config = json.load(f)

openLoad = config['openLoad']
nowPage = openLoad
theme = config['theme'] if 'theme' in config else 'standard'
debug = True if config['enableDebug'] == 'on' else False

games = dict(bh3='1', ys='2', bh2='3', wd='4', dby='5', sr='6', zzz='8')
gamesById = ['bh3', 'ys', 'bh2', 'wd', 'dby', 'sr', '', 'zzz']
gamesName = {'bh3': '崩坏3', 'ys': '原神', 'bh2': '崩坏学园2', 'wd': '未定事件簿', 'dby': '大别野',
             'sr': '崩坏：星穹铁道', '': '空', 'zzz': '绝区零'}
token = webview.token
appUserAgent = f'HoMoLab/114.514 (token-{token})'
firstAccess = True

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
                return func(*args, **kwargs)
            else:
                try:
                    resp = make_response(func(*args, **kwargs))
                    resp.set_cookie('token', token)
                    if firstAccess:
                        firstAccess = False
                    return resp
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
    return render_template('article.html', thread=thread, type=render_method, game=game)


# 文章评论
@app.route('/comments')
@LoadPage
def comments():
    post_id = request.args.get("id")
    gid = request.args.get("gid")
    page = request.args.get("page") if 'page' in request.args else '1'
    replies = libhoyolab.Comments(post_id=post_id, gid=gid, page=page)
    return render_template('comment.html', thread=replies)


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
                           select='recommend', game=game, page=page, isLast=False)


# 搜索
@app.route('/<game>/search')
@LoadPage
def search(game):
    content = request.args.get('content')
    gameid = games[game]
    page = int('1' if 'page' not in request.args else request.args.get('page'))
    search_result = libhoyolab.Search(keyWords=content, gid=gameid, page=page)
    return render_template('main.html', articles=search_result.getArticles(), search=content,
                           select='search', game=game, page=page, isLast=search_result.isLastFlag)


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
                           select=requestType, game=game, page=page)


@app.route('/setting', methods=['POST', 'GET'])
@LoadPage
def setting():
    global config, nowPage, openLoad
    if request.method == 'GET':
        return render_template('settings.html', game=nowPage, isSaved=False, config=config)
    else:
        logging.info("the new settings had been uploaded!")
        settings = request.form.to_dict()
        for k in settings:
            config[k] = settings[k]
        openLoad = config['openLoad']
        nowPage = openLoad
        window.set_title(f'米游社 - {gamesName[openLoad]}')
        with open('configs/config.json', mode='w+') as fp:
            json.dump(config, fp)
            logging.info(fp.read())
        return render_template('settings.html', game=nowPage, isSaved=True, config=config)


# 跳转到原神分区
@app.route('/')
@LoadPage
def index():
    window.set_title(f'米游社 - {gamesName[openLoad]}')
    return redirect(f'/{openLoad}')


if __name__ == '__main__':
    if platform.system() == 'Windows':
        try:
            window = webview.create_window('米游社', app, min_size=(650, 800), width=1280, height=1000)
            webview.start(gui="edgechromium", user_agent=appUserAgent, debug=debug)

        except KeyError:
            # （我也不知道关闭窗口为什么会弹KeyError
            pass

        except KeyboardInterrupt:
            pass

        except:
            # 如果用户系统中没有EdgeWebview的话，则弹窗提示用户安装环境
            root = Tk()
            root.withdraw()
            messagebox.showerror(title="运行环境错误", message="请检查当前系统环境是否支持 EdgeWebview2")

    else:
        # 如果系统不是windows的话，则弹窗提示用户不兼容
        root = Tk()
        root.withdraw()
        messagebox.showerror(title="运行环境错误", message="当前应用仅支持在Windows环境下运行")
