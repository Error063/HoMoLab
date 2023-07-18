# encoding:utf-8
import pprint

from flask import Flask, render_template, request
import webview
import libhoyolab


app = Flask(__name__)

@app.route('/article')
def article():  # put application's code here
    post_id = request.args.get("id")
    thread = libhoyolab.Article(post_id=post_id)
    render_method = thread.getRenderType()
    return render_template('article.html', thread=thread, type=render_method)

@app.route('/comments')
def comments():
    post_id = request.args.get("post_id")
    gid = request.args.get("gid")
    replies = libhoyolab.Comments(post_id=post_id, gid=gid)
    return render_template('comment.html', thread=replies)

@app.route('/')
def main():
    return render_template('main.html', articles=libhoyolab.MainPage(gid="2").getArticles())

if __name__ == '__main__':
    app.run()
