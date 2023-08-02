# post_id="41214610"
# article = libhoyolab.Article(post_id)
# print(article.getTitle())
# print(article.getAuthor())
# # html = threadRender.render(article.getStructuredContent())
# # with open("opt.html", mode="w", encoding="utf8") as f:
# #     f.write(html)
from libhoyolab import *
import urllib3
import json
import requests

_USERAGENT = 'Mozilla/5.0 (Linux; Android 13; M2101K9C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/108.0.5359.128 Mobile Safari/537.36 miHoYoBBS/2.51.1'

urllib3.disable_warnings()

headers = {
    "User-Agent": _USERAGENT,
    "x-rpc-client_type": "5",
    "x-rpc-sys_version": "13",
    "x-rpc-channel": "xiaomi",
    "x-rpc-device_name": "Xiaomi M2101K9C",
    "X-Requested-With": "com.mihoyo.hyperion",
    "x-rpc-app_id": "bll8iq97cem8",
    "Referer": "https://webstatic.mihoyo.com",
}
cookie_dict = dict()

if __name__ == '__main__':
    cookie = accountLogin.login()
    while "cookie_token_v2" not in cookie[0].lower():
        cookie = accountLogin.login()
    pprint.pprint(cookie[1])
    print(headers)
    a = requests.get(f"https://bbs-api.miyoushe.com/user/api/getUserFullInfo", headers=headers, cookies=cookie[1])
    j = a.json()
    print(j)