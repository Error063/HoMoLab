# encoding:utf-8
import pprint

from flask import Flask, render_template, request
import webview
import libhoyolab

# import io
# import sys
#
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')

app = Flask(__name__)

names: dict = {'ys': '原神', 'sr': '崩坏：星穹铁道', 'bh3': '崩坏3', 'no': '本地来源'}  # 游戏代码与其相对应的可读文字


@app.route('/article')
def article():  # put application's code here
    post_id = request.args.get("id")
    thread = libhoyolab.Article(post_id=post_id)
    render_method = thread.getRenderType()
    match render_method:
        case 1:
            return render_template('article.html', thread=thread)
        case 2:
            return render_template('picture.html', thread=thread)
        case 5:
            return "<script>alert('目前尚不支持视频内容播放');window.history.back()</script>"
        case _:
            return "<script>alert('类型错误！');window.history.back()</script>"


@app.route('/comments')
def comments():
    post_id = request.args.get("post_id")
    gid = request.args.get("gid")
    replies = libhoyolab.Comments(post_id=post_id, gid=gid)
    return render_template('comment.html', thread=replies)


@app.route('/')
def main():
    return render_template('main.html', articles=libhoyolab.MainPage(gid="2").getArticles())


# class Apis:
#     """
#     提供给Javascript的Python API
#     """
#     def closeApp(self):
#         """
#         关闭窗口
#         :return:
#         """
#         window.destroy()
#
#     def minimizeApp(self):
#         """
#         窗口最小化
#         :return:
#         """
#         window.minimize()
#
#     def executePython(self, cmd):
#         """
#         在Javascript中执行Python语句
#         :param cmd:
#         :return:
#         """
#         exec(cmd)


if __name__ == '__main__':
    app.run()
