import urllib.request, re
# 参数是一个字典{'类型':'代理ip:端口号'}
proxy_support = urllib.request.ProxyHandler({'http': '183.217.223.149:8123'})
# 定制、创建一个opener
opener = urllib.request.build_opener(proxy_support)
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2150.5 Safari/537.36')]
a = opener.open('http://whatismyip.com.tw/')
b = a.read().decode('utf-8')
bid_re = re.search('<h1>IP位址</h1> <h2>(.+?)</h2>', b)
print(bid_re.group(1))
