# -*- coding: utf-8 -*-
import urllib.request, re
def getreviews(bids, uids):
	html = urllib.request.urlopen('http://www.douban.com/people/%s/reviews' % (uids))
	html = html.read().decode('utf-8')
	reviews_num = re.search('的评论\((.+?)\)</h1>', html)
	reviews_num = int(reviews_num.group(1))
	n = 1
	while reviews_num > 5 * (n - 1):
		html = urllib.request.urlopen('http://www.douban.com/people/%s/reviews?&start=%d' % (uids, 5 * (n - 1)))
		html = html.read().decode('utf-8')
		# 单个评论页面链接
		url = re.finditer('<a href="http://book.douban.com/subject/(.+?)/">', html)
		for u in url:
			result_list.append([bids, uids, u])
		if deep_int <= deep_r:
				mainprocess(bids) 
		n += 1
def mainprocess(bids):
	global deep_int
	deep_int += 1
	html = urllib.request.urlopen('http://book.douban.com/subject/%s/reviews' % (bids))
	html = html.read().decode('utf-8')
	# 总评论数量
	reviews_num = re.search('的评论 \((.+?)\)</h1>', html)
	reviews_num = int(reviews_num.group(1))
	n = 1
	while reviews_num > 25 * (n - 1):
		html = urllib.request.urlopen('http://book.douban.com/subject/%s/reviews?score=&start=%d' % (bids, 25 * (n - 1)))
		html = html.read().decode('utf-8')
		# 单个评论页面链接
		url = re.finditer('<a href="http://book.douban.com/people/(.+?)/" class=" ">', html)
		for u in url:
			getreviews(bids, u.group(1))
		n += 1
deep_r = 1 # 设定深度
deep_int = 0 ##
result_list = []
mainprocess('5686369')
print(result_list)
