# -*- coding: utf-8 -*-import feedparser as fp, re# 获取用户评论过的图书IDdef getreviews(bids, uids):	f = fp.parse('http://www.douban.com/feed/people/%s/reviews' % (uids))	for j in f['items']:		item_link = j.link		if item_link.startswith('http://book.douban.com/review/'):			item_des = j.description			bid_re = re.search('book.douban.com/subject/(.+?)/', item_des)			bid = bid_re.group(1)			result_list.append([bids, uids, bid])# 获取评论过图书的用户IDdef mainprocess(bids):	d = fp.parse('http://book.douban.com/feed/subject/%s/reviews' % (bids))	for i in d['items']:		item_con = i.content[0]['value']		uid_re = re.search('//book.douban.com/people/(.+?)/">', item_con)		uid = uid_re.group(1)		getreviews(bids, uid)# 执行程序result_list = []mainprocess('5686369')print(result_list)