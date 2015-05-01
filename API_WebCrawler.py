# encoding: UTF-8
import os, urllib.request, json, sys, re, http.cookiejar, urllib.parse
from wsgiref.simple_server import make_server, demo_app
import threading, time, pickle, random, xml.dom.minidom

# �û���Ϣ
user_email = '949100761@qq.com'
user_password = 'hbc075786780743'
# API Key
api_key = '0232ffd2601070310698ff7720315093'
# Secret
secret_code = '5cb9d363193cc5ad'
# �ص���ַ
redirect_uri = 'http://127.0.0.1'
# scope ���ŷָ�
scope = 'shuo_basic_r,shuo_basic_w,douban_basic_common'
# douban url
douban_url = 'https://www.douban.com/'
# douban api url
doubanapi_url = 'https://api.douban.com/'

# web_server�߳�
class Webserver(threading.Thread):
	"""docstring for Webserver"""
	def __init__(self):
		super().__init__()
		self.httpd = make_server('', 80, demo_app)
	def run(self):
		self.httpd.serve_forever()
		time.sleep(5)
		self.httpd.shutdown()

# ����webserver
def webstart():
	webs = Webserver()
	webs.start()

def check_pyversion():
	version = sys.version
	if not version.startswith('3.4'):
		print('��ʹ��python3.4�汾�򿪱�����')
		input()
		print('����ʹ�õ���python %s' % (version))
		sys.exit()

# ��ʼ������
def init_web():
	# ����cookie
	webCookie = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
	openner = urllib.request.build_opener(webCookie)
	# ����header
	openner.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2150.5 Safari/537.36')]
	# urllib.request.install_opener(openner) 

	return openner

# ������վ
def url_open(openner, url, datas = None):
	if datas is not None:
		datas = urllib.parse.urlencode(datas).encode('utf-8')
		response = openner.open(url, datas)
	else:
		response = openner.open(url)
	html = response.read()

	return (html, response.geturl())

def login_in(form_email, form_password):
	# ��ʼ��
	web_openner = init_web()
	login_url = douban_url + 'accounts/login'
	params = {}
	params['form_email'] = form_email
	params['form_password'] = form_password
	params['source'] = 'index_nav'	
	html, response_url = url_open(web_openner, login_url, params)
	html = html.decode('utf-8')

	if response_url == login_url:
		#��֤��ͼƬ��ַ
		img_url = re.search('<img id="captcha_image" src="(.+?)" alt="captcha" class="captcha_image"/>', html)
		if img_url:
			url = img_url.group(1)
			# ����ͼƬ
			urllib.request.urlretrieve(url, 'v.jpg')
			captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>' ,html)
			if captcha:
				vcode = input('������ͼƬ�ϵ���֤�룺')
				params["captcha-solution"] = vcode
				params["captcha-id"] = captcha.group(1)
				params["user_login"] = "��¼"
				html, response_url = url_open(web_openner, login_url, params)
				if response_url in('http://www.douban.com/', douban_url):
					print('��½�ɹ�')
				else:
					print('ʧ����')
				os.remove('v.jpg')

# ��ȡauthorization_code
def get_authcode(form_email, form_password, scopes = scope):
	# ��ʼ��
	web_openner = init_web()
	authcode_url = douban_url + 'service/auth2/auth?client_id=' + api_key + '&redirect_uri=' + redirect_uri + '&response_type=code'
	if scopes:
		authcode_url = authcode_url + '&scope=' + scopes
	params = {}
	params['user_alias'] = form_email
	params['user_passwd'] = form_password
	params['confirm'] = '��Ȩ'
	# ����webserver
	webstart()
	html, response_url = url_open(web_openner, authcode_url, params)
	response_url += '//'
	get_code = re.search('/?code=(.+?)/', response_url)
	if get_code:
		print('�ɹ����authorization_code')
		authcode = get_code.group(1)
	else:
		print('��ȡʧ��')
		authcode = ''

	return authcode

# ��ȡaccess_token
def get_accesroken(authcodes):
	accesroken_url = douban_url + 'service/auth2/token'
	data = {}
	data['client_id'] = api_key
	data['client_secret'] = secret_code
	data['redirect_uri'] = redirect_uri
	data['grant_type'] = 'authorization_code'
	data['code'] = authcodes
	# ����webserver
	webstart()
	accesroken_html, response_url = url_open(web_openner, accesroken_url, data)
	accesroken_json = json.loads(accesroken_html.decode('utf-8'))

	return accesroken_json

# ˢ��access_token
def refresh_accesroken(old_accesroken_json):
	accesroken_url = douban_url + 'service/auth2/token'
	data = {}
	data['client_id'] = api_key
	data['client_secret'] = secret_code
	data['redirect_uri'] = redirect_uri
	data['grant_type'] = 'refresh_token'
	data['refresh_token'] = old_accesroken_json['refresh_token']
	# ����webserver
	webstart()
	accesroken_html, response_url = url_open(web_openner, accesroken_url, data)
	accesroken_json = json.loads(accesroken_html.decode('utf-8'))

	return accesroken_json

# ������
def error_deter(result_json):
	if result_json['code']:
		if result_json['code'] == 106:
			print('access_token�ѹ���,׼������')
			accetoken_json = refresh_accesroken(accetoken_json)
			print('access_token����Ϊ %s' % (accetoken_json['access_token']))
			return 1
		else:
			print(result_json['msg'])
			return 1
	else:
		return 0

# get proxy list
def get_proxy_list():
	proxy_url = 'http://cn-proxy.com/'
	accesroken_html, response_url = url_open(web_openner, proxy_url)
	html = accesroken_html.decode('utf-8')
	proxy_list = re.findall('<tr>\n<td>(.+?)</td>\n<td>(\d+)</td>', html)
	return proxy_list

def proxy_open_url(urls, accetoken_jsons, proxy_url_lists):
	webCookie = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
	proxy_ip_port = random.choice(proxy_url_lists)
	proxy_support = urllib.request.ProxyHandler({'http': ':'.join(proxy_ip_port)})
	openner = urllib.request.build_opener(webCookie, proxy_support)
	
	openner.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2150.5 Safari/537.36')]
	openner.addheaders = [('Authorization', 'Bearer %s' % (accetoken_jsons['access_token']))]
	req = openner.open(urls)
	return req

def getreviews(bids, uids):
	url = '%s/%s/reviews' % (p_url, uids)
	html = proxy_open_url(url, accetoken_json, proxy_url_list)
	DOMTree = xml.dom.minidom.parseString(html.read().decode('utf-8'))
	feed = DOMTree.getElementsByTagName( "feed" )[0]
	rbook = feed.getElementsByTagName( "opensearch:totalResults" )[0].childNodes[0].nodeValue
	m = 1
	while int(rbook) > 50 * (m-1):
		url = '%s/%s/reviews?max-results=50&start-index=%d' % (p_url, uids, 50 * (m-1) + 1)
		html = proxy_open_url(url, accetoken_json, proxy_url_list)
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
				if deep_int <= deep_r: # ����ж�ѭ��
					mainprocess(bid) ##
def mainprocess(bids):
	global deep_int ##
	deep_int += 1 ##
	url = '%s/%s/reviews' % (base_url, bids)
	html = proxy_open_url(url, accetoken_json, proxy_url_list)
	html = json.loads(html.read().decode('utf-8'))
	reviews_num = html['total']
	n = 1
	while reviews_num > 100 * (n-1):
		url = '%s/%s/reviews?count=100&start=%d' % (base_url, bids, 100 * (n-1))
		html = proxy_open_url(url, accetoken_json, proxy_url_list)
		html = json.loads(html.read().decode('utf-8'))
		for i in html['reviews']:
			a = i['author']
			getreviews(bids, a['uid'])
		n += 1

# main
def test_main():
	# ���Python�汾
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

	proxy_url_list = get_proxy_list()

	base_url = 'http://api.douban.com/v2/book'
	p_url = 'http://api.douban.com/people'
	deep_r = 3 # �趨���
	deep_int = 0 ##
	result_list = []
	mainprocess('5686369')
	print(result_list)

if __name__ == '__main__':
	test_main()

