import json
import os
import re
from datetime import date, datetime
import operator

modelVersion = 1

def createDisplayName(name):
    keywords = ['request filled', 'request fulfillment', 'completed request', 'script requested', 'script request',
                'first script', 'pornhub', 'request']
    for keyword in keywords:
        name = re.sub('[\(]\s*' + keyword + '\s*\[\)]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub('[\[]\s*' + keyword + '\s*\]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub('\s*' + keyword + '\s*[\:]?[\-]?\s*', '', name, flags=re.IGNORECASE)
    return name.strip()

EXCLUDED_SITES = [ "eporner"]
def save_index(sourceIndexFile, indexFileName):
    if os.path.exists(sourceIndexFile):
        with open(sourceIndexFile) as f:
            data = json.load(f)
    else:
        data = {}
        data['author'] = 'xqueezeme'
        data['videos'] = []
        data['tags'] = []
    data['version'] = modelVersion
    videos = data['videos']
    newVideos = []
    tags = {}
    print("Upgrading script videos")
    for idx, video in enumerate(videos):
        if (video.get('ignore', False) == False and video.get('valid', True) and video.get('site') not in EXCLUDED_SITES):
            video['displayName'] = createDisplayName(video.get('name'))
            for tag in video['tags']:
                newTags = tags.get(tag)
                if (newTags == None):
                    newTags = []
                newTags.append(video['name'])
                tags[tag] = newTags
            newVideos.append(video)
    print(f"Active videos: {len(newVideos)}")
    data['videos'] = newVideos
    data['tags'] = dict(sorted(tags.items(), key=operator.itemgetter(0)))

    jsonStr = json.dumps(data)
    with open(indexFileName, "w") as outfile:
        outfile.write(jsonStr)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.try_datetime, *args, **kwargs)

    @staticmethod
    def try_datetime(d):
        ret = {}
        for key, value in d.items():
            try:
                ret[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                ret[key] = value
        return ret