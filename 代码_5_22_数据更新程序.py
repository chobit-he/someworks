# -*- coding: utf-8 -*-
import urllib.request, re, time
def updatabookreview(bids):
	html = urllib.request.urlopen('http://book.douban.com/subject/%s/reviews?sort=time' % (bids))
	html = html.read().decode('utf-8')
	# 总评论数量
	reviews_num = re.search('的评论 \((.+?)\)</h1>', html)
	reviews_num = int(reviews_num.group(1))
	n = 1
	while reviews_num > 25 * (n - 1):
		html = urllib.request.urlopen('http://book.douban.com/subject/%s/reviews?sort=time&score=&start=%d' % (bids, 25 * (n - 1)))
		html = html.read().decode('utf-8')
		url = re.finditer('<a href="http://book.douban.com/people/(.+?)/" class=" ">(?:[\w\W]+?)<div class="pl clearfix">\n                    <span class="fleft">\n                        <span class="">(.+?)</span> &nbsp; &nbsp;\n                    </span>', html)
		for u in url:
			utime = time.mktime(time.strptime(u.group(2),'%Y-%m-%d %H:%M'))
			if utime < last_time:return 0
			print(bids, u.group(1))
		n += 1
last_time = 1406732980.0 # 上次更新时间
updatabookreview('4718495')
