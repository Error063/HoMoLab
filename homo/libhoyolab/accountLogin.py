"""
用户登录
"""
import json
import os
import pathlib
import time

import webview
import requests

from homo.libhoyolab import urls

cookies = ''
loginPageDestroyed_user = False
home_dir = str(pathlib.Path.home())
run_dir = os.path.join(home_dir, 'homolab-dir')
config_dir = os.path.join(run_dir, 'configs')
account_file = os.path.join(config_dir, 'account.json')

page = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <style>
        button{
            height: 50px;
            width: 150px;
            border: none;
        }
        *{
            margin: 10px auto 0 10px;
        }
    </style>
    <script>
        function afterShowLoginPage() {
            pywebview.api.tologin().then(
                function (flag) {
                    if(flag['flag']){
                        document.getElementsByClassName('login_user')[0].setAttribute("style","display: none")
                        document.getElementsByClassName('end')[0].setAttribute("style","display: block")
                    }else {
                        alert("尝试显示窗口失败，请关闭该窗口后再试")
                    }
                }
            )
        }
        function afterLoginSuccess_user() {
            let status = confirm("是否登录完毕？");
            if (status){
                pywebview.api.getcookies_user().then(
                    function (flag) {
                        console.log(flag['flag'])
                        if(flag['flag']){
                            document.getElementsByClassName('end')[0].setAttribute("style","display: none")
                            document.getElementsByClassName('step')[0].setAttribute("style","display: none")
                            document.getElementsByClassName('ableToClose')[0].setAttribute("style","display: block")
                        }else {
                            alert('尝试获取登录参数错误，请重新登录！')
                        }
                    }
                )
            }
        }
    </script>
</head>
<body>
    <p><button class="login_user" onclick="afterShowLoginPage()" style="display: block">登录通行证</button></p>
    <p><button class="end" onclick="afterLoginSuccess_user()" style="display: none">完成</button></p>
    <h1 class="ableToClose" style="display: none">现在可以关闭该页面了</h1>
    <p class="step" style="margin: 0 auto;">步骤：在打开通行证页面后,登录通行证</p>
</body>
</html>"""


def loginByWeb():
    """
    利用pywebview处理用户登录事件并将获取到的login_ticket写入到account.json中
    """
    global cookies

    class apis:
        def tologin(self):
            global loginPageDestroyed_user
            if not loginPageDestroyed_user:
                loginAccount_user.show()
                return {'flag': True}
            else:
                main.create_confirmation_dialog(title="错误", message="尝试打开米游社时出错，请稍后重试")
                main.destroy()
                return {'flag': False}

        def getcookies_user(self):
            global loginPageDestroyed_user, cookies
            tmp = loginAccount_user.evaluate_js("document.cookie")

            if "login_ticket" in tmp:
                cookies += tmp
                loginAccount_user.confirm_close = False
                main.confirm_close = False
                loginAccount_user.destroy()
                loginPageDestroyed_user = True
                for c in cookies.split(" "):
                    if 'login_ticket' in c:
                        cookies = c
                        break
                with open(account_file, mode='r') as fp:
                    account = json.load(fp)
                with open(account_file, mode='w+') as fp:
                    account['login_ticket'] = cookies.split('=')[-1]
                    json.dump(account, fp)
                return {'flag': True}
            else:
                return {'flag': False}

    api = apis()
    loginAccount_user = webview.create_window(title="!!!完成登录操作前请勿关闭该窗口!!!",
                                              url="https://user.mihoyo.com", hidden=True,
                                              confirm_close=True, height=900, width=900)
    main = webview.create_window(js_api=api, on_top=True, x=10, y=10, title='!!!完成登录操作前请勿关闭该窗口!!!',
                                 html=page, minimized=False, confirm_close=True, resizable=False)
    return cookies


def loginByPassword(account, password):
    """
    使用账号密码进行登录
    :param account: 账号
    :param password: 密码
    :return:
    """
    session = requests.session()
    resp_mmt = session.get(urls.mmt_pwd.format(int(time.time() * 1000), account, int(time.time() * 1000))).json()
    if 'risk_type' in resp_mmt['data']:
        return {'msg': '当前账号无法直接使用该方式登录', 'token': ''}
    else:
        mmt_key = resp_mmt['data']['mmt_data']['mmt_key']
        datas = {
            'account': account,
            'password': password,
            'is_crypto': 'false',
            'mmt_key': mmt_key,
            'source': 'user.mihoyo.com',
            't': str(int(time.time() * 1000))
        }
        raw_resp = session.post(urls.login, data=datas)
        resp_login = raw_resp.json()
        if resp_login['data']['msg'] == '成功':
            return {'msg': resp_login['data']['msg'], 'token': resp_login['data']['account_info']['weblogin_token']}
        else:
            return {'msg': resp_login['data']['msg'], 'token': ''}
