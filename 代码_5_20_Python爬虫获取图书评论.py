# -*- coding: utf-8 -*-
import urllib.request, re
from 代码_3_4_Python获取RSS格式的数据_增加深度 import deepprocess # 导入方法
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
		for bid in url:
			result_list.append([bids, uids, bid.group(1), deep_int])
		n += 1
def mainprocess(bids):
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
deep_int = 0
result_list = []
deepprocess('4718495', 2)
print(result_list)
