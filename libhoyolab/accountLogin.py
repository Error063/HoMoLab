import webview

cookies_str = ''
cookies_dic = dict()
loginPageDestroyed = False


def login():
    global cookies_str, cookies_dic
    class apis:
        def tologin(self):
            global loginPageDestroyed
            if not loginPageDestroyed:
                loginAccount.show()
                return {'flag': True}
            else:
                return {'flag': False}

        def getcookies(self):
            global cookies_str, cookies_dic, loginPageDestroyed
            cookies = loginAccount.get_cookies()
            for cookie in cookies:
                ck = cookie.output(header='')
                cookies_str += ck[1:] + "; "
                c = ck[1:].split('; ')[0].split('=')
                cookies_dic[c[0]] = c[1]
            # print(cookies_str)
            if "login_ticket" in cookies_str:
                loginAccount.destroy()
                loginPageDestroyed = True
                return {'flag': True}
            else:
                return {'flag': False}

    api = apis()
    loginAccount = webview.create_window(title="!!!完成登录操作前请勿关闭该窗口!!!",
                                         url="https://user.mihoyo.com/#/account/home", hidden=True,
                                         confirm_close=True, height=1300, width=1000)
    main = webview.create_window(js_api=api, on_top=True, x=10, y=10, title='!!!完成登录操作前请勿关闭该窗口!!!',
                                 html=open(
                                     "../templates/login.html", encoding='utf8').read(), minimized=False,
                                 confirm_close=True)
    webview.start(debug=True, private_mode=False)
    return cookies_str, cookies_dic
