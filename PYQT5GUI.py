from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import time
import urllib.request, json, xml.dom.minidom
import feedparser as fp, re

class firstWindows(QtWidgets.QMainWindow):
	def __init__(self,parent = None):
		super().__init__()
		self.setWindowTitle('获取豆瓣图书数据的三种方法')
		
		self.statusBar().showMessage('就绪')
		
		menubar = self.menuBar()
		file_mb = menubar.addMenu('&文件')
		how_mb = menubar.addMenu('&?')
		
		exit_mb = QtWidgets.QAction("退出", self, shortcut="Ctrl+Q", triggered = self.close)
		about_mb = QtWidgets.QAction("关于", self, shortcut="F1", triggered = self.aboutff)
		
		file_mb.addAction(exit_mb)
		how_mb.addAction(about_mb)
		
		screen = QtWidgets.QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width() - size.width()) / 2,
		(screen.height() - size.height()) / 2)
		
		rss_bt = QtWidgets.QPushButton('RSS', self)
		api_bt = QtWidgets.QPushButton('API', self)
		wc_bt = QtWidgets.QPushButton('爬虫', self)
		close_bt = QtWidgets.QPushButton('退出', self)
		
		rss_bt.clicked.connect(self.rssff)
		api_bt.clicked.connect(self.apiff)
		wc_bt.clicked.connect(self.wbff)
		close_bt.clicked.connect(self.close)
		
		id_lb = QtWidgets.QLabel('图书ID：', self)
		deep_lb = QtWidgets.QLabel('获取深度：', self)
		self.id_le = QtWidgets.QLineEdit(self)
		self.deep_sb = QtWidgets.QSpinBox(self)
		self.viewcode_cb = QtWidgets.QCheckBox('查看源码')
		self.viewcode_cb.setChecked(True)
		
		rss_bt.setStatusTip('使用RSS获取豆瓣网图书数据')
		api_bt.setStatusTip('使用API获取豆瓣网图书数据')
		wc_bt.setStatusTip('使用爬虫获取豆瓣网图书数据')
		close_bt.setStatusTip('退出程序')
		self.id_le.setPlaceholderText('请输入图书ID')
		self.deep_sb.setMinimum(1)
		self.viewcode_cb.setStatusTip('勾选后，仅查看源代码')

		widget = QtWidgets.QWidget()
		hbox1 = QtWidgets.QHBoxLayout()
		hbox2 = QtWidgets.QHBoxLayout()
		
		hbox1.addStretch(0)
		hbox1.addWidget(rss_bt)
		hbox1.addWidget(api_bt)
		hbox1.addWidget(wc_bt)
		hbox1.addWidget(close_bt)
		hbox2.addWidget(id_lb)
		hbox2.addWidget(self.id_le)
		hbox2.addWidget(deep_lb)
		hbox2.addWidget(self.deep_sb)
		hbox2.addWidget(self.viewcode_cb)
		
		vbox = QtWidgets.QVBoxLayout()

		self.textEdit = QtWidgets.QTextEdit(self)
		
		vbox.addLayout(hbox2)
		vbox.addWidget(self.textEdit)
		vbox.addLayout(hbox1)

		widget.setLayout(vbox)
		self.setCentralWidget(widget)

	def rssff(self):
		if self.viewcode_cb.isChecked():
			self.textEdit.setText('开始读取源代码')
			self.textEdit.append('')
			self.showcode('代码_3_3_Python获取RSS格式的数据')
			self.showcode('代码_3_4_Python获取RSS格式的数据_增加深度')
			self.textEdit.append('源代码结束')
		else:
			book_id = self.id_le.text()
			deep_i = self.deep_sb.value()
			self.textEdit.setText('输入的图书ID为：%s，深度设置为：%s'%(book_id, deep_i))
			self.textEdit.append('开始执行程序...')
			
			global mainprocess
			def mainprocess(bids):
				d = fp.parse('http://book.douban.com/feed/subject/%s/reviews' % (bids))
				for i in d['items']:
					item_con = i.content[0]['value']
					uid_re = re.search('//book.douban.com/people/(.+?)/">', item_con)
					uid = uid_re.group(1)
					getreviews(bids, uid)
			
			def getreviews(bids, uids):
				f = fp.parse('http://www.douban.com/feed/people/%s/reviews' % (uids))
				for j in f['items']:
					item_link = j.link
					if item_link.startswith('http://book.douban.com/review/'):
						item_des = j.description
						bid_re = re.search('book.douban.com/subject/(.+?)/', item_des)
						bid = bid_re.group(1)
						result_list.append([bids, uids, bid, deep_int])
					
			time1 = time.time()
			global deep_int
			deep_int = 0
			result_list = []
			
			try:
				deepprocess(book_id, deep_i)
			except:pass
			
			for i in result_list:
				self.textEdit.append('%s  %s' % (i[0], i[1]))
			self.textEdit.append('')
			time2 = time.time()
			self.textEdit.append('获取%d条评论链接，耗时%10.10f，平均%10.10f每条'%(len(result_list),(time2 - time1),((time2 - time1)/len(result_list))))
			
	def apiff(self):
		if self.viewcode_cb.isChecked():
			self.textEdit.setText('开始读取源代码')
			self.textEdit.append('')
			self.showcode('代码_4_16_获取豆瓣API的数据')
			self.textEdit.append('源代码结束')
		else:
			book_id = self.id_le.text()
			deep_i = self.deep_sb.value()
			self.textEdit.setText('输入的图书ID为：%s，深度设置为：%s'%(book_id, deep_i))
			self.textEdit.append('开始执行程序...')
			
			def open_url(urls):
				req = urllib.request.Request(urls)
				html = urllib.request.urlopen(req)
				return html
				
			def getreviews(bids, uids):
				url = '%s/%s/reviews' % (p_url, uids)
				html = open_url(url)
				DOMTree = xml.dom.minidom.parseString(html.read().decode('utf-8'))
				feed = DOMTree.getElementsByTagName( "feed" )[0]
				rbook = feed.getElementsByTagName( "opensearch:totalResults" )[0].childNodes[0].nodeValue
				m = 1
				while int(rbook) > 50 * (m-1):
					url = '%s/%s/reviews?max-results=50&start-index=%d' % (p_url, uids, 50 * (m-1) + 1)
					m += 1
					html = open_url(url)
					DOMTree = xml.dom.minidom.parseString(html.read().decode('utf-8'))
					feed = DOMTree.getElementsByTagName( "feed" )[0]
					entry = feed.getElementsByTagName( "entry" )
					for i in entry:
						subject = i.getElementsByTagName( "db:subject" )[0]
						lbid = subject.getElementsByTagName( "id" )[0].childNodes[0].nodeValue
						if lbid.startswith('http://api.douban.com/book/subject/'):
							bid = lbid[35:]
							result_list.append([bids, uids, bid, deep_int])
							
			global mainprocess
			def mainprocess(bids):
				url = '%s/%s/reviews' % (base_url, bids)
				html = open_url(url)
				html = json.loads(html.read().decode('utf-8'))
				reviews_num = html['total']
				n = 1
				while reviews_num > 100 * (n-1):
					url = '%s/%s/reviews?count=100&start=%d' % (base_url, bids, 100 * (n-1))
					html = open_url(url)
					html = json.loads(html.read().decode('utf-8'))
					for i in html['reviews']:
						a = i['author']
						getreviews(bids, a['uid'])
					n += 1
					
			acc_headers = {'Authorization': 'Bearer a14afef0f66fcffce3e0fcd2e34f6ff4'}
			base_url = 'https://api.douban.com/v2/book'
			p_url = 'https://api.douban.com/people'
					
			time1 = time.time()
			global deep_int
			deep_int = 0
			result_list = []
			try:
				deepprocess(book_id, deep_i)
			except:pass
			for i in result_list:
				self.textEdit.append('%s  %s' % (i[0], i[1]))
			self.textEdit.append('')
			time2 = time.time()
			self.textEdit.append('获取%d条评论链接，耗时%10.10f，平均%10.10f每条'%(len(result_list),(time2 - time1),((time2 - time1)/len(result_list))))
		
	def wbff(self):
		if self.viewcode_cb.isChecked():
			self.textEdit.setText('开始读取源代码')
			self.textEdit.append('')
			self.showcode('代码_5_20_Python爬虫获取图书评论')
			self.textEdit.append('源代码结束')
		else:
			book_id = self.id_le.text()
			deep_i = self.deep_sb.value()
			self.textEdit.setText('输入的图书ID为：%s，深度设置为：%s'%(book_id, deep_i))
			self.textEdit.append('开始执行程序...')
			
			def getreviews(bids, uids):
				html = urllib.request.urlopen('http://www.douban.com/people/%s/reviews' % (uids))
				html = html.read().decode('utf-8')
				reviews_num = re.search('的评论\((.+?)\)</h1>', html)
				reviews_num = int(reviews_num.group(1))
				n = 1
				while reviews_num > 5 * (n - 1):
					html = urllib.request.urlopen('http://www.douban.com/people/%s/reviews?&start=%d' % (uids, 5 * (n - 1)))
					html = html.read().decode('utf-8')
					url = re.finditer('<a href="http://book.douban.com/subject/(.+?)/">', html)
					for bid in url:
						result_list.append([bids, uids, bid.group(1), deep_int])
					n += 1
			
			global mainprocess
			def mainprocess(bids):
				html = urllib.request.urlopen('http://book.douban.com/subject/%s/reviews' % (bids))
				html = html.read().decode('utf-8')
				reviews_num = re.search('的评论 \((.+?)\)</h1>', html)
				reviews_num = int(reviews_num.group(1))
				n = 1
				while reviews_num > 25 * (n - 1):
					html = urllib.request.urlopen('http://book.douban.com/subject/%s/reviews?score=&start=%d' % (bids, 25 * (n - 1)))
					html = html.read().decode('utf-8')
					url = re.finditer('<a href="http://book.douban.com/people/(.+?)/" class=" ">', html)
					for u in url:
						getreviews(bids, u.group(1))
					n += 1
					
			time1 = time.time()
			global deep_int
			deep_int = 0
			result_list = []
			try:
				deepprocess(book_id, deep_i)
			except:pass
			for i in result_list:
				self.textEdit.append('%s  %s' % (i[0], i[1]))
			self.textEdit.append('')
			time2 = time.time()
			self.textEdit.append('获取%d条评论链接，耗时%10.10f，平均%10.10f每条'%(len(result_list),(time2 - time1),((time2 - time1)/len(result_list))))

	def showcode(self, strs):
		self.textEdit.append('"%s"源代码' % (strs))
		file = open('%s.py' % (strs),'r',encoding= 'utf8')
		data = file.read()
		self.textEdit.append(data)

	def closeEvent(self, event):
		reply = QtWidgets.QMessageBox.question(self, '警告',
		"真的要离开么?", QtWidgets.QMessageBox.Yes,
		QtWidgets.QMessageBox.No)
		if reply == QtWidgets.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()
		
	def aboutff(self):
		reply = QtWidgets.QMessageBox.about(self, '关于',
		"程序为毕业论文示例（作者：何成标）\nhttps://github.com/chobit-he/someworks")
	
def deepprocess(bids, deep_r):
	global deep_int
	while 1:
		if deep_int == 0:
			deep_int += 1
			mainprocess(bids)
		elif deep_int < deep_r:
			deep_int += 1
			for k in result_list:
				if k[3] == deep_int - 1: mainprocess(k[2])
		else: break
#### 4718495

def mainWindows():
	app = QtWidgets.QApplication(sys.argv)
	win1 = firstWindows()

	win1.show()

	sys.exit(app.exec_())

if __name__ == "__main__":
	mainWindows()