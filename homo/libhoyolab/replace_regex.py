"""
正则表达式规则集
"""
emotion = r"_\((.*?)\)"
article = r'<a href="https://(?:www\.miyoushe|bbs\.mihoyo)\.com/\w{2,3}/article/(\d+)".+?target="_blank"'
user = r'<a href="https://(?:www\.miyoushe|bbs\.mihoyo)\.com/\w{2,3}/accountCenter/\w{0,14}\?id=(\d+)".+?target="_blank"'