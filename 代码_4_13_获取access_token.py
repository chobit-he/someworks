import urllib.request, json, urllib.parse
accesroken_url = 'https://www.douban.com/service/auth2/token'
data = {}
data['client_id'] = '0232ffd2601070310698ff7720315093'
data['client_secret'] = '5cb9d363193cc5ad'
data['redirect_uri'] = ' https://www.example.com/back '
data['grant_type'] = 'authorization_code'
data['code'] = '9b73a4248'
data = urllib.parse.urlencode(data).encode('utf-8')
accesroken_html = urllib.request.urlopen (accesroken_url, data)
accesroken_json = json.loads(accesroken_html.read().decode('utf-8'))