# encoding:utf-8
import os
import pprint
from functools import wraps
from flask import Flask, render_template, request, redirect, make_response, send_file, url_for, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import libhoyolab
import webview

with open('configs/config.json') as f:
    config = json.load(f)

openLoad = config['openLoad']
nowPage = openLoad

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

games = dict(bh3='1', ys='2', bh2='3', wd='4', dby='5', sr='6', zzz='8')
gamesById = ['bh3', 'ys', 'bh2', 'wd', 'dby', 'sr', '', 'zzz']
gamesName = {'bh3': '崩坏3', 'ys': '原神', 'bh2': '崩坏学园2', 'wd': '未定事件簿', 'dby': '大别野',
             'sr': '崩坏：星穹铁道', '': '空', 'zzz': '绝区零'}
token = webview.token
appUserAgent = f'HoMoLab/114.514 (token-{token})'
firstAccess = True
browser = True


def LoadPage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global firstAccess, nowPage
        print("=" * 15)
        print(f"access url: {request.url}")
        print(f"remote ip: {request.remote_addr}")
        print(f"user agent: {request.user_agent.string}")
        userAgent = request.user_agent.string
        if userAgent != appUserAgent and ((request.cookies['token'] != token) or firstAccess):
            print('browser that not allowed')
            return "<h1>app鉴权失败！</h1>", 403
        else:
            return func(*args, **kwargs)
            # try:
            #     resp = make_response(func(*args, **kwargs))
            #     resp.set_cookie('token', token)
            #     if firstAccess:
            #         firstAccess = False
            #     return resp
            # except Exception as e:
            #     print(f"Error! {e}")
            #     return "<p><h1>尝试处理请求时出现错误！</h1></p><p><button onclick='window.location.reload()'>重试</button></p>"

    return wrapper


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'icons/appicon.ico', mimetype='image/vnd.microsoft.icon')

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
    page = int(request.args.get('page') if 'page' in request.args else '1')
    return render_template('main.html', articles=libhoyolab.Page(gid=games[game], page=page, pageType='recommend').getArticles(),
                           select='recommend', game=game, page=page, isLast=False)


# 搜索
@app.route('/<game>/search')
@LoadPage
def search(game):
    content = request.args.get('content')
    gameid = games[game]
    page = int(request.args.get('page') if 'page' in request.args else '1')
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
    page = request.args.get('page') if 'page' in request.args else '1'
    return render_template('main.html', articles=libhoyolab.Page(gid=games[game], page=page, pageType=requestType).getArticles(),
                           select=requestType, game=game)


@app.route('/setting', methods=['POST', 'GET'])
def setting():
    global config, nowPage, openLoad
    if request.method == 'GET':
        return render_template('settings.html', game=nowPage, isSaved=False, config=config)
    else:
        settings = request.form.to_dict()
        print(settings)
        for k in settings:
            config[k] = settings[k]
        print(config)
        openLoad = config['openLoad']
        nowPage = openLoad
        window.set_title(f'米游社 - {gamesName[openLoad]}')
        with open('configs/config.json', mode='w') as fp:
            json.dump(config, fp)
        return render_template('settings.html', game=nowPage, isSaved=True, config=config)


# 跳转到原神分区
@app.route('/')
@LoadPage
def index():
    window.set_title(f'米游社 - {gamesName[openLoad]}')
    return redirect(f'/{openLoad}')


if __name__ == '__main__':
    window = webview.create_window('米游社', app, min_size=(650, 800), width=1280, height=1000)
    webview.start(user_agent=appUserAgent, debug=True if config['enableDebug'] == 'on' else False)
