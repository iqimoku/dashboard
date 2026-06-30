import json, sys

with open('user_response.json') as f:
    data = json.load(f)

if 'data' not in data:
    print("BLAD API:", json.dumps(data, indent=2), file=sys.stderr)
    sys.exit(1)

print(data['data']['id'])
