import json
import time

import requests


options = {
        "gonewildstories": { 'tags': ['straight'] },
        "nsfwstories": { 'tags': ['straight'] },
        "eroticliterature": { 'tags': ['straight'] },
        "gonewholesomestories": { 'tags': ['straight'] },
        "gaystoriesgonewild": { 'tags': ['gay']},
        "gaysexconfessions": { 'tags': ['gay']},
        "gaystories": { 'tags': ['gay']},
        "gayconfessions": { 'tags': ['gay']},
        "tsgonewildstories": { 'tags': ['trans']},
        "cdstoriesgonewild": { 'tags':['cd']},
        "crossdressingstories": { 'tags':['cd']},
        "bistoriesgonewild": { 'tags':['bi']},
        "sluttyconfessions": { 'tags':['straight','slut']},
        "femdomstories": { 'tags':['femdom']},
        "naughtynarratives":{ 'tags':['straight','slut']},
        "stupidslutsclub":{ 'tags':['straight','slut']},
        "cheating_stories":{ 'tags':['straight','slut']},
        "chastitystories": { 'tags': ["chastity","sissy"]},
        "sexstories": { 'tags': ["straight"]},
        "bdsmerotica": { 'tags': ["femdom"]},
        "cuckoldstories2": { 'tags': ["straight"]},
        "breedingstories": { 'tags': ["straight"]}
}
def is_valid_subreddit(subreddit: str):
    response = requests.get(f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50")

    return response.status_code == 200

image_reddits = {'straight': ['gonewild', 'GoneWild30Plus', 'PetiteGoneWild', 'GoneWildCurvy', 'GWNerdy', 'gonewildsmiles', 'bdsmgw', 'AnalGW'],
                 'slut': ['cumsluts'],
                 'gay': ['gaygw', 'GayBrosGoneWild', 'mangonewild'],
                 'trans': ['gonewildtrans', 'Shemales', 'tscumsluts', 'ShemalesParadise', 'Shemale_Big_Cock', 'traps'],
                 'cd': ['gonewildcd', 'crossdressing', 'sissychastity'], 'chastity': ['sissychastity'], 'bi': ['bigonewild', 'BisexualFantasy'],
                 'femdom': ['femdomgonewild', 'FemdomSelfies'],
                 'sissy': ['sissies', 'traps', 'FemBoys']}
new_image_reddits = {}
for k, v in image_reddits.items():
    subrs = []
    for r in v:
        if is_valid_subreddit(r):
            subrs.append(r)
        time.sleep(5)
    new_image_reddits[k] = subrs
valid_subreddits = []
for subreddit, subreddit_conf in options.items():
    if is_valid_subreddit(subreddit):
        valid_subreddits.append(subreddit)
    time.sleep(5)

valid_subreddits = sorted(valid_subreddits)
subreddit_with_images = {}
for valid_subreddit in valid_subreddits:
    image_sub_reddits = set()
    for tag in options.get(valid_subreddit).get('tags', []):
        for r in new_image_reddits.get(tag, []):
            image_sub_reddits.add(r)
    subreddit_with_images[valid_subreddit] = list(image_sub_reddits)

print("options = " + json.dumps(list(subreddit_with_images.keys()), indent=4))

print("var imageReddits = " + json.dumps(subreddit_with_images, indent=4)  + ";")

print("var defaultImageReddit = " + json.dumps(new_image_reddits['straight'], indent=4)+ ";")
