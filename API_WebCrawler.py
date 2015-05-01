# encoding: UTF-8
import os, urllib.request, json, sys, re, http.cookiejar, urllib.parse
from wsgiref.simple_server import make_server, demo_app
import threading, time, pickle, random, xml.dom.minidom

# 用户信息
user_email = '949100761@qq.com'
user_password = 'hbc075786780743'
# API Key
api_key = '0232ffd2601070310698ff7720315093'
# Secret
secret_code = '5cb9d363193cc5ad'
# 回调地址
redirect_uri = 'http://127.0.0.1'
# scope 逗号分隔
scope = 'shuo_basic_r,shuo_basic_w,douban_basic_common'
# douban url
douban_url = 'https://www.douban.com/'
# douban api url
doubanapi_url = 'https://api.douban.com/'

# web_server线程
class Webserver(threading.Thread):
	"""docstring for Webserver"""
	def __init__(self):
		super().__init__()
		self.httpd = make_server('', 80, demo_app)
	def run(self):
		self.httpd.serve_forever()
		time.sleep(5)
		self.httpd.shutdown()

# 运行webserver
def webstart():
	webs = Webserver()
	webs.start()

def check_pyversion():
	version = sys.version
	if not version.startswith('3.4'):
		print('请使用python3.4版本打开本程序')
		input()
		print('你所使用的是python %s' % (version))
		sys.exit()


# 初始化网络
def init_web():
	# 加入cookie
	webCookie = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
	# ip_list = []
	# proxy_support = urllib.request.ProxyHandler({'http': random.choice(ip_list)})
	openner = urllib.request.build_opener(webCookie)
	# 加入header
	openner.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2150.5 Safari/537.36')]
	# urllib.request.install_opener(openner) 

	return openner

# 访问网站
def url_open(openner, url, datas = None):
	if datas is not None:
		datas = urllib.parse.urlencode(datas).encode('utf-8')
		response = openner.open(url, datas)
	else:
		response = openner.open(url)
	html = response.read()

	return (html, response.geturl())

def login_in(form_email, form_password):
	# 初始化
	web_openner = init_web()
	login_url = douban_url + 'accounts/login'
	params = {}
	params['form_email'] = form_email
	params['form_password'] = form_password
	params['source'] = 'index_nav'	
	html, response_url = url_open(web_openner, login_url, params)
	html = html.decode('utf-8')

	if response_url == login_url:
		#验证码图片地址
		img_url = re.search('<img id="captcha_image" src="(.+?)" alt="captcha" class="captcha_image"/>', html)
		if img_url:
			url = img_url.group(1)
			# 下载图片
			urllib.request.urlretrieve(url, 'v.jpg')
			captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>' ,html)
			if captcha:
				vcode = input('请输入图片上的验证码：')
				params["captcha-solution"] = vcode
				params["captcha-id"] = captcha.group(1)
				params["user_login"] = "登录"
				html, response_url = url_open(web_openner, login_url, params)
				if response_url in('http://www.douban.com/', douban_url):
					print('登陆成功')
				else:
					print('失败了')
				os.remove('v.jpg')

# 获取authorization_code
def get_authcode(form_email, form_password, scopes = scope):
	# 初始化
	web_openner = init_web()
	authcode_url = douban_url + 'service/auth2/auth?client_id=' + api_key + '&redirect_uri=' + redirect_uri + '&response_type=code'
	if scopes:
		authcode_url = authcode_url + '&scope=' + scopes
	params = {}
	params['user_alias'] = form_email
	params['user_passwd'] = form_password
	params['confirm'] = '授权'
	# 运行webserver
	webstart()
	html, response_url = url_open(web_openner, authcode_url, params)
	response_url += '//'
	get_code = re.search('/?code=(.+?)/', response_url)
	if get_code:
		print('成功获得authorization_code')
		authcode = get_code.group(1)
	else:
		print('获取失败')
		authcode = ''

	return authcode

# 获取access_token
def get_accesroken(authcodes):
	accesroken_url = douban_url + 'service/auth2/token'
	data = {}
	data['client_id'] = api_key
	data['client_secret'] = secret_code
	data['redirect_uri'] = redirect_uri
	data['grant_type'] = 'authorization_code'
	data['code'] = authcodes
	# 运行webserver
	webstart()
	accesroken_html, response_url = url_open(web_openner, accesroken_url, data)
	accesroken_json = json.loads(accesroken_html.decode('utf-8'))

	return accesroken_json

# 刷新access_token
def refresh_accesroken(old_accesroken_json):
	accesroken_url = douban_url + 'service/auth2/token'
	data = {}
	data['client_id'] = api_key
	data['client_secret'] = secret_code
	data['redirect_uri'] = redirect_uri
	data['grant_type'] = 'refresh_token'
	data['refresh_token'] = old_accesroken_json['refresh_token']
	# 运行webserver
	webstart()
	accesroken_html, response_url = url_open(web_openner, accesroken_url, data)
	accesroken_json = json.loads(accesroken_html.decode('utf-8'))

	return accesroken_json

# 错误检测
def error_deter(result_json):
	if result_json['code']:
		if result_json['code'] == 106:
			print('access_token已过期,准备更新')
			accetoken_json = refresh_accesroken(accetoken_json)
			print('access_token更新为 %s' % (accetoken_json['access_token']))
			return 1
		else:
			print(result_json['msg'])
			return 1
	else:
		return 0

# main
def test_main():
	# 检查Python版本
	check_pyversion()

	if os.path.exists('accetoken.plk'):
		accetoken_file = open('accetoken.plk','rb')
		accetoken_json = pickle.load(accetoken_file)
		accetoken_file.close()
	else:
		login_in(user_email, user_passwd)
		authcode = get_authcode(user_email, user_passwd)
		accetoken_json = get_accesroken(authcode)
		accetoken_file = open('accetoken.plk','wb')
		pickle.dump(accetoken_json, accetoken_file)
		accetoken_file.close()

	web_openner.addheaders = [('Authorization', 'Bearer %s' % (accetoken_json['access_token']))]


	


if __name__ == '__main__':
	test_main()





def getreviews(bids, uids):
	url = '%s/%s/reviews' % (p_url, uids)
	html, response_url = url_open(url)
	DOMTree = xml.dom.minidom.parseString(html.read().decode('utf-8'))
	feed = DOMTree.getElementsByTagName( "feed" )[0]
	rbook = feed.getElementsByTagName( "opensearch:totalResults" )[0].childNodes[0].nodeValue
	m = 1
	while int(rbook) > 50 * (m-1):
		url = '%s/%s/reviews?max-results=50&start-index=%d' % (p_url, uids, 50 * (m-1) + 1)
		html, response_url = url_open(url)
		DOMTree = xml.dom.minidom.parseString(html.read().decode('utf-8'))
		feed = DOMTree.getElementsByTagName( "feed" )[0]
		entry = feed.getElementsByTagName( "feed" )
		for i in entry:
			subject = i.getElementsByTagName( "db:subject" )[0]
			lbid = subject.getElementsByTagName( "id" )[0].childNodes[0].nodeValue
			if lbid.startswith('http://book.douban.com/review/'):
				bid_re = re.search('book.douban.com/subject/(.+?)/', lbid)
				bid = bid_re.group(1)
				result_list.append([bids, uids, bid])
				if deep_int <= deep_r: # 深度判定循环
					mainprocess(bid) ##
def mainprocess(bids):
	global deep_int ##
	deep_int += 1 ##
	url = '%s/%s/reviews' % (base_url, bids)
	html, response_url = url_open(url)
	html = json.loads(html.read().decode('utf-8'))
	reviews_num = html['total']
	n = 1
	while reviews_num > 100 * (n-1):
		url = '%s/%s/reviews?count=100&start=%d' % (base_url, bids, 100 * (n-1))
		html, response_url = url_open(url)
		html = json.loads(html.read().decode('utf-8'))
		for i in html['reviews']:
			a = i['author']
			getreviews(bids, a['uid'])
		n += 1
headers = {'Authorization' : 'Bearer a14afef0f66fcffce3e0fcd2e34f6ff4'}
base_url = 'http://api.douban.com/v2/book'
p_url = 'http://api.douban.com/people'
deep_r = 3 # 设定深度
deep_int = 0 ##
result_list = []
mainprocess('5686369')
print(result_list)