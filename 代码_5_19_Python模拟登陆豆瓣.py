import urllib.request, http.cookiejar
# 加入cookie
webCookie = http.cookiejar.CookieJar()
openner = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(webCookie))
urllib.request.install_opener(openner)
login_url = ' https://www.douban.com/accounts/login '
params = {}
params['form_email'] = '{username}'
params['form_password'] = '{userpassword}'
params['source'] = 'index_nav'	
params = urllib.parse.urlencode(params).encode('utf-8')
html = openner.open(login_url, params)	
if html.geturl() in('http://www.douban.com/', 'https://www.douban.com/'):
	print('登陆成功')
else:
	print('失败了')
