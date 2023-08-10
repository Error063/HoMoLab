"""
将文章的部分内容（表情包、指向米游社的部分链接）进行替换
"""
import json
import re

from libhoyolab import replace_regex


def replaceAllFromDelta(contents: list | str, emotionDict: dict):
    """
    将表情包文本进行转义
    :param contents: 结构化文章内容
    :param emotionDict: 表情包集合
    :return:
    """
    if type(contents) is str:
        contents = json.loads(contents)
    new_contents = list()
    for content in contents:
        if type(content['insert']) is str:
            emotions = re.findall(replace_regex.emotion, content['insert'])
            if len(emotions) > 0:
                for emotion in emotions:
                    new_contents.append({'insert': {'image': emotionDict[emotion], "attributes": {"height": 100, "width": 100}}})
            else:
                new_contents.append(content)
        else:
            new_contents.append(content)

    return json.dumps(new_contents, ensure_ascii=False)


def replaceAll(contents: str, emotionDict: dict):
    """
    将文章的部分内容（表情包、指向米游社的部分链接）进行替换
    :param contents: 文章内容
    :param emotionDict: 表情包集合
    :return:
    """
    contents = re.sub(replace_regex.emotion,
                      lambda m: f'<img class="emoticon-image emotionIcon" src="{emotionDict[m.group(1)]}">',
                      contents)
    contents = re.sub(replace_regex.article, lambda m: f'<a href="/article?id={m.group(1)}">', contents)
    contents = re.sub(replace_regex.user, lambda m: f'<a href="/user?uid={m.group(1)}">', contents)
    return contents
