# -*- coding: utf-8 -*-import timetime1 = time.time()# 开始时间try:	'''数据获取程序（RSS/API/Web crawler）'''except:passtime2 = time.time()# 结束时间print('获取%d条评论链接，耗时%10.10f，平均%10.10f每条'%(len(result_list),(time2 - time1),((time2 - time1)/len(result_list))))