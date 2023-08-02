import webview
import os

cookies = None
cookies_str = ''
cookies_dic = dict()
loginPageDestroyed = False

page = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <style>
        button{
            height: 50px;
            width: 150px;
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
                        document.getElementsByClassName('tologin')[0].setAttribute("style","display: none")
                        document.getElementsByClassName('getcookies')[0].setAttribute("style","display: block")
                    }else {
                        alert("尝试显示窗口失败，请关闭该窗口后再试")
                    }
                }
            )
        }
        function afterLoginSuccess() {
            let status = confirm("是否登录完毕？");
            if (status){
                pywebview.api.getcookies().then(
                    function (flag) {
                        console.log(flag['flag'])
                        if(flag['flag']){
                            document.getElementsByClassName('getcookies')[0].setAttribute("style","display: none")
                            document.getElementsByClassName('step')[0].setAttribute("style","display: none")
                            document.getElementsByClassName('ableToClose')[0].setAttribute("style","display: block")
                        }else {
                            alert('尝试获取登录参数错误，请重新登录！')
                            document.getElementsByClassName('getcookies')[0].setAttribute("style","display: none")
                            document.getElementsByClassName('tologin')[0].setAttribute("style","display: block")
                        }
                    }
                )
            }
        }
    </script>
</head>
<body>
    <p><button class="tologin" onclick="afterShowLoginPage()" style="display: block">先点击我</button></p>
    <p><button class="getcookies" onclick="afterLoginSuccess()" style="display: none">登录完成后再点击我</button></p>
    <h1 class="ableToClose" style="display: none">现在可以关闭该页面了</h1>
    <p class="step" style="margin: 0 auto;">步骤：在打开米游社后,点击头像登录即可</p>
</body>
</html>"""


def login():
    global cookies_str, cookies_dic, cookies
    print(__file__)

    class apis:
        def tologin(self):
            global loginPageDestroyed
            if not loginPageDestroyed:
                loginAccount.show()
                return {'flag': True}
            else:
                main.create_confirmation_dialog(title="错误", message="尝试打开米游社时出错，请稍后重试")
                main.destroy()
                return {'flag': False}

        def getcookies(self):
            global cookies_str, cookies_dic, loginPageDestroyed, cookies
            cookies = loginAccount.get_cookies()

            cookies_str = ''
            cookies_dic = dict()
            for cookie in cookies:
                ck = cookie.output(header='')
                cookies_str += ck[1:] + "; "
                c = ck[1:].split('; ')[0].split('=')
                cookies_dic[c[0]] = c[1]
            # print(cookies_str)
            if "cookie_token_v2" in cookies_str:
                loginAccount.confirm_close = False
                main.confirm_close = False
                loginAccount.destroy()
                loginPageDestroyed = True
                return {'flag': True}
            else:
                return {'flag': False}

    api = apis()
    loginAccount = webview.create_window(title="!!!完成登录操作前请勿关闭该窗口!!!",
                                         url="https://www.miyoushe.com/ys/", hidden=True,
                                         confirm_close=True, fullscreen=True)
    main = webview.create_window(js_api=api, on_top=True, x=10, y=10, title='!!!完成登录操作前请勿关闭该窗口!!!',
                                 html=page, minimized=False,
                                 confirm_close=True)
    webview.start(debug=False)
    return cookies_str, cookies_dic
