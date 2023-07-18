import requests
import json
import urllib3

urllib3.disable_warnings()

def getEmotions(gid='2'):
    print('emotion lib is running')
    emodict = dict()
    req = requests.get(f"https://bbs-api-static.miyoushe.com/misc/api/emoticon_set?gid={gid}", verify=False)
    contents = json.loads(req.content.decode("utf8"))['data']['list']

    for emoset in contents:
        for emotion in emoset['list']:
            emodict[emotion['name']] = emotion['icon']

    return emodict


class Emotions:
    def __init__(self, gid=2):
        print('emotion lib is running')
        self.emodict = dict()
        req = requests.get(f"https://bbs-api-static.miyoushe.com/misc/api/emoticon_set?gid={gid}", verify=False)
        contents = json.loads(req.content.decode("utf8"))['data']['list']

        for emoset in contents:
            for emotion in emoset['list']:
                self.emodict[emotion['name']] = emotion['icon']

    def getEmotion(self, name):
        print(f'getting {name}')
        try:
            return self.emodict[name]
        except KeyError:
            return ''
