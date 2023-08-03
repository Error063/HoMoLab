# encoding:utf-8
import pprint
from functools import wraps
from flask import Flask, render_template, request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import user_agents as ua
import libhoyolab

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

games = dict(bh3='1', ys='2', bh2='3', wd='4', dby='5', sr='6', zzz='8')


def LoadPage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("=" * 15)
        print(f"access url: {request.url}")
        print(f"remote ip: {request.remote_addr}")
        print(f"user agent: {request.user_agent.string}")
        userAgent = ua.parse(request.user_agent.string)
        if userAgent.browser.family == "IE":
            print("IE detected")
            return "<h1>不支持IE浏览器！</h1>"
        else:
            # return func(*args, **kwargs)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error! {e}")
                return "<p><h1>尝试处理请求时出现错误！</h1></p><p><button onclick='window.location.reload()'>重试</button></p>"

    return wrapper


@app.route('/article')
@LoadPage
def article():
    post_id = request.args.get("id")
    thread = libhoyolab.Article(post_id=post_id)
    render_method = thread.getRenderType()
    return render_template('article.html', thread=thread, type=render_method)


@app.route('/comments')
@LoadPage
def comments():
    post_id = request.args.get("id")
    gid = request.args.get("gid")
    page = request.args.get("page") if 'page' in request.args else '1'
    replies = libhoyolab.Comments(post_id=post_id, gid=gid, page=page)
    return render_template('comment.html', thread=replies)


@app.route('/<game>')
@LoadPage
def main(game):
    return render_template('main.html', articles=libhoyolab.Page(gid=games[game], pageType='recommend').getArticles(),
                           select='recommend', game=game)


@app.route('/search')
@LoadPage
def search():
    content = request.args.get('content')
    return f'你搜索了{content}'


@app.route('/<game>/news')
@LoadPage
def news(game):
    requestType = request.args.get('type') if 'type' in request.args else 'announce'
    return render_template('main.html', articles=libhoyolab.Page(gid=games[game], pageType=requestType).getArticles(),
                           select=requestType,game=game)

@app.route('/')
def index():
    return redirect('/ys')

if __name__ == '__main__':
    app.run(debug=True)
