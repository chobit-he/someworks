# encoding: UTF-8
import os, urllib.request, json, sys, re, http.cookiejar, urllib.parse
from wsgiref.simple_server import make_server, demo_app
import threading, time

# 用户信息
form_email = '949100761@qq.com'
form_password = 'hbc075786780743'
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

# 版本要求
def check_pyversion():
	version = sys.version
	if not version.startswith('3.4'):
		print('请使用python3.4版本打开本程序')
		input()
		sys.exit()
	print('你所使用的是python %s' % (version))

# 初始化网络
def init_web():
	# 加入cookie
	webCookie = http.cookiejar.CookieJar()
	openner = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(webCookie))
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

def login_in():
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
def get_authcode(scopes = scope):
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
	check_pyversion()
	login_in()
	authcode = get_authcode()
	accetoken_json = get_accesroken(authcode)
	#{'douban_user_name': 'chobit', 'refresh_token': 'ba69e4ab3d73b3232f3dae01b85b1969', 'access_token': '27d6cfb7b23afb0377846f2716b0f109', 'expires_in': 604800, 'douban_user_id': '71884854'}
	# 加入头文件
	# web_openner.addheaders = [('Authorization', 'Bearer %s' % (accetoken_json['access_token']))]























# 参数处理
def add_param(url, param_dict):
	url += '?'
	first0 = 0
	for i in param_dict:
		if first0 == 0:
			url = url + i + '=' + param_dict[i]
			first0 = 1
			continue
		url = url + '&'+ i + '=' + param_dict[i]
	
	return url
# 访问
def open2json(url, datas = None):
	html = url_open(web_openner, url, datas)[0]
	result_json = json.loads(html.decode('utf-8'))
	if error_deter(result_json):
		result_json = json.loads(html.decode('utf-8'))

	return result_json

# DETEL method
def del_method(url):
	openner.open(web_openner, url, method = 'DELETE')

# PUT method
def put_method(url, datas):
	datas = urllib.parse.urlencode(datas).encode('utf-8')
	openner.open(web_openner, url, datas, method = 'PUT')

'''
图书Api V2
'''
class book_api_v2():
	"""docstring for book_api_v2"""

	# scope: book_basic_r
	# 获取图书信息
	def book_id(self, ids):
		urls = doubanapi_url + 'v2/book/' + ids
		result_json = open2json(urls)
		
		return result_json
	# 根据isbn获取图书信息
	def book_isbn(self, names):
		urls = doubanapi_url + 'v2/book/isbn/' + names
		result_json = open2json(urls)
		
		return result_json
		

'''
搜索图书	GET	/v2/book/search
获取某个图书中标记最多的标签	GET	/v2/book/:id/tags
获取用户对图书的所有标签	GET	/v2/book/user/:name/tags
获取某个用户的所有图书收藏信息	GET	/v2/book/user/:name/collections
获取用户对某本图书的收藏信息	GET	/v2/book/:id/collection
获取某个用户的所有笔记	GET	/v2/book/user/:name/annotations
获取某本图书的所有笔记	GET	/v2/book/:id/annotations
获取某篇笔记的信息	GET	/v2/book/annotation/:id
获取丛书书目信息	GET	/v2/book/series/:id/books

用户收藏某本图书	POST	/v2/book/:id/collection
用户修改对某本图书的收藏	PUT	/v2/book/:id/collection
用户删除对某本图书的收藏	DELETE	/v2/book/:id/collection
用户给某本图书写笔记	POST	/v2/book/:id/annotations
用户修改某篇笔记	PUT	/v2/book/annotation/:id
用户删除某篇笔记	DELETE	/v2/book/annotation/:id

发表新评论	POST	/v2/book/reviews
修改评论	PUT	/v2/book/review/:id
删除评论	DELETE	/v2/book/review/:id
获取用户对图书的所有标签(deprecated)	GET	/v2/book/user_tags/:id
'''




'''
论坛API V2
'''
class furm_api_v2():
	"""docstring for furm_api_v2"""
	
	# scope: douban_common_basic
	# 获取讨论
	def get_discussion(self, ids):		
		urls = doubanapi_url + 'v2/discussion/'+ ids		
		result_json = open2json(urls)

		return result_json
	# 更新讨论
	def re_discussion(self, ids, title, content):		
		urls = doubanapi_url + 'v2/discussion/'+ ids
		data={'title':title, 'content':content}		
		put_method(urls, data)

	def del_discussion(self, ids):		
		urls = doubanapi_url + 'v2/discussion/'+ ids		
		del_method(urls)

	# scope具体见target的文档，target指论坛所依附的产品对象名称


'''
新发讨论	POST	/v2/target/:id/discussions
获取讨论列表	GET	/v2/target/:id/discussions
'''


'''
回复Api V2
'''
class repo_api_v2():
	"""docstring for repo_api_v2"""
	
	# scope具体见target的文档，target指回复所依附的产品对象名称
	# 获取回复列表
	def get_comments(self, ids, start = '', count = ''):
		param_dict = {'start':start,'count':count}
		urls = doubanapi_url + 'v2/target/'+ ids + '/comments'
		urls = add_param(urls, param_dict)
		result_json = open2json(urls)
		
		return result_json
	# 新发回复
	def post_comments(self, ids, content):
		datas = {'content':content}
		urls = doubanapi_url + 'v2/target/'+ ids + '/comments'
		result_json = open2json(urls, datas)
		
		return result_json
	# 获取单条回复
	def get_comment(self, ids, com_id):
		urls = doubanapi_url + 'v2/target/'+ ids + '/comments/' + com_id
		result_json = open2json(urls)
		
		return result_json

	# 删除回复
	def del_comment(self, ids, com_id):
		urls = doubanapi_url + 'v2/target/'+ ids + '/comments/' + com_id
		del_method(urls)

'''
我去Api V2
'''
class igo_api_v2():
	"""docstring for igo_api_v2"""
	
	# scope: travel_basic_r
	# 获取某个用户的地点收藏
	def travel_user(self, names, status = '', start = '', count = ''):
		param_dict = {'status':status,'start':start,'count':count}
		urls = doubanapi_url + 'v2/travel/user/'+ names + '/collections'
		urls = add_param(urls, param_dict)
		result_json = open2json(urls)
		
		return result_json
	# 获取地点信息
	def travel_place(self, ids, status = '', start = '', count = ''):
		param_dict = {'status':status,'start':start,'count':count}
		urls = doubanapi_url + 'v2/travel/place/' + ids
		urls = add_param(urls, param_dict)
		result_json = open2json(urls)
		
		return result_json



if __name__ == '__main__':
	test_main()
