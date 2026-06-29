import json, datetime

with open('tweets_raw.json') as f:
    data = json.load(f)

data['_updated'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
data['_username'] = 'SteveDJacobs'

with open('tweets.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Zapisano', len(data.get('data', [])), 'tweetow')
