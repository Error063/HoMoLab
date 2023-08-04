# encoding:utf-8
import pprint
from functools import wraps
from flask import Flask, render_template, request, redirect, make_response, send_file, url_for
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
            # return func(*args, **kwargs)
            try:
                resp = make_response(func(*args, **kwargs))
                resp.set_cookie('token', token)
                if firstAccess:
                    firstAccess = False
                return resp
            except Exception as e:
                if str(e) == "'favicon.ico'":
                    print('requiring favicon')
                    return url_for('static', filename='pics/exampleUser.jpg')
                else:
                    print(f"Error! {e}")
                    return "<p><h1>尝试处理请求时出现错误！</h1></p><p><button onclick='window.location.reload()'>重试</button></p>"

    return wrapper


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
    return render_template('main.html', articles=libhoyolab.Page(gid=games[game], pageType='recommend').getArticles(),
                           select='recommend', game=game)


# 搜索
@app.route('/search')
@LoadPage
def search():
    content = request.args.get('content')
    return f'你搜索了{content}'


# 官方资讯
@app.route('/<game>/news')
@LoadPage
def news(game):
    global nowPage
    nowPage = game
    requestType = request.args.get('type') if 'type' in request.args else 'announce'
    return render_template('main.html', articles=libhoyolab.Page(gid=games[game], pageType=requestType).getArticles(),
                           select=requestType, game=game)


@app.route('/setting', methods=['POST', 'GET'])
def setting():
    global config
    if request.method == 'GET':
        return render_template('settings.html', game=nowPage, isSaved=False, config=config)
    else:
        settings = request.form.to_dict()
        print(settings)
        for k in settings:
            config[k] = settings[k]
        print(config)
        with open('configs/config.json', mode='w') as fp:
            json.dump(config, fp)
        return render_template('settings.html', game=nowPage, isSaved=True, config=config)


# 跳转到原神分区
@app.route('/')
@LoadPage
def index():
    return redirect(f'/{openLoad}')


if __name__ == '__main__':
    window = webview.create_window('米游社', app, min_size=(650, 800), width=1280, height=1000)
    webview.start(user_agent=appUserAgent, debug=True if config['enableDebug'] == 'on' else False)
