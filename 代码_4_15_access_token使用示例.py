import urllib.request, json
acc_headers = { 'Authorization' : 'Bearer a14afef0f66fcffce3e0fcd2e34f6ff4' }
req = urllib.request.Request(url, data = None, headers = acc_headers)
response = urllib.request.urlopen(req)
json_data = json.loads(response.read().decode('utf-8'))
