import feedparser
import json
import datetime
import sys

# Lista instancji Nitter jako fallback
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.lucabased.xyz",
]

USERNAME = "YahooFinance"

def try_fetch(instance):
    url = f"{instance}/{USERNAME}/rss"
    print(f"Próba: {url}")
    feed = feedparser.parse(url)
    if feed.bozo and not feed.entries:
        print(f"  Błąd: {feed.bozo_exception}")
        return None
    if not feed.entries:
        print(f"  Brak wpisów")
        return None
    print(f"  OK — {len(feed.entries)} tweetów")
    return feed

feed = None
for instance in NITTER_INSTANCES:
    feed = try_fetch(instance)
    if feed:
        break

if not feed:
    print("BŁĄD: Żadna instancja Nitter nie odpowiada!")
    # Zapisz pusty JSON żeby nie crashował strony
    data = {
        "_updated": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "_username": USERNAME,
        "_error": "Nie można pobrać tweetów — wszystkie instancje Nitter niedostępne",
        "data": []
    }
    with open('tweets.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    sys.exit(0)

# Parsuj wpisy RSS do formatu zgodnego z index.html
tweets = []
for entry in feed.entries[:20]:
    # Wyciągnij tekst — usuń HTML tagi
    import re
    content = entry.get('summary', entry.get('title', ''))
    # Usuń obrazki i inne HTML
    content = re.sub(r'<img[^>]+>', '', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = content.strip()

    # Data
    published = entry.get('published_parsed')
    if published:
        dt = datetime.datetime(*published[:6])
        created_at = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        created_at = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # ID z linka
    link = entry.get('link', '')
    tweet_id = link.split('/')[-1].split('#')[0] if link else ''

    tweets.append({
        "id": tweet_id,
        "text": content,
        "created_at": created_at,
        "public_metrics": {
            "like_count": 0,
            "retweet_count": 0,
            "reply_count": 0,
            "impression_count": 0
        }
    })

# Dane autora z RSS
feed_info = feed.feed
author_name = feed_info.get('title', 'Yahoo Finance').replace(' / Nitter', '').strip()

data = {
    "data": tweets,
    "includes": {
        "users": [{
            "id": "yahoofinance",
            "name": author_name,
            "username": USERNAME,
            "profile_image_url": ""
        }]
    },
    "_updated": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    "_username": USERNAME
}

with open('tweets.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Zapisano {len(tweets)} tweetów")
