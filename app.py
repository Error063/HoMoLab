# encoding:utf-8
import pprint
from functools import wraps
from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import user_agents as ua
import libhoyolab

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
def LoadPage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("="*15)
        print(f"access url: {request.url}")
        print(f"remote ip: {request.remote_addr}")
        print(f"user agent: {request.user_agent.string}")
        userAgent = ua.parse(request.user_agent.string)
        if userAgent.browser.family == "IE":
            print("IE detected")
            return "<h1>不支持IE浏览器！</h1>"
        else:
            return func(*args, **kwargs)
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
    post_id = request.args.get("post_id")
    gid = request.args.get("gid")
    replies = libhoyolab.Comments(post_id=post_id, gid=gid)
    return render_template('comment.html', thread=replies)


@app.route('/')
@LoadPage
def main():
    return render_template('main.html', articles=libhoyolab.MainPage(gid="2").getArticles())


if __name__ == '__main__':
    app.run()
