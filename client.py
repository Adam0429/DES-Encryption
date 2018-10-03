import socket
import threading
import json
from cmd import Cmd
from des import _des
import wx

class MyFrame(wx.Frame):	#创建自定义Frame
	prompt = ''
	intro = '[Welcome] 简易聊天室客户端(Cli版)\n' + '[Welcome] 输入help来获取帮助\n'

	def __init__(self,parent):
		#def __init__(
		# self, parent=None, id=None, title=None, pos=None,
		# size=None, style=None, name=None)
		wx.Frame.__init__(self,parent,id=-1,title="Hello World",size=(390,300),pos=(0,0)) #设置窗体
		panel = wx.Panel(self)
	
		
		self.inputText = wx.TextCtrl(panel,-1,"",pos=(0,210),size=(150,20))
		self.outputText = wx.TextCtrl(panel,-1,"",pos=(0,0),size=(350,200))
		self.key = wx.TextCtrl(panel,-1,"",pos=(200,210),size=(150,20))

		# self.quitbtn = wx.Button(panel,-1,"send",pos=(500,500))
		self.sendbtn = wx.Button(panel,-1,"send",pos=(0,230))
		self.encryptbtn = wx.Button(panel,-1,"decrypt",pos=(200,230))

		self.inputText.SetInsertionPoint(0) #设置焦点位置
		self.sendbtn.Bind(wx.EVT_BUTTON,self.send)   #绑定鼠标进入事件
		self.encryptbtn.Bind(wx.EVT_BUTTON,self.encrypt)
		self.Center()   #将窗口放在桌面环境的中间

		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__id = None
		self.__nickname = None
		self.__status = 0

		self.start()
		self.do_login()

		

	def __receive_message_thread(self):
		"""
		接受消息线程
		"""
		while True:
			# noinspection PyBroadException
			# try:
			
			buffer = self.__socket.recv(1024).decode()      # 没有消息时这里堵塞
			result = ''
			if self.__status:
				text = self.outputText.GetValue().split('\r')
				for t in text:
					if t.strip() != '':
						result = result + _des(t,self.key.GetValue(),self.__status) + '\n'
				self.outputText.SetValue(result)
				self.__status = 0
				self.encryptbtn.SetLabelText('decrypt')
			obj = json.loads(buffer)
			if self.outputText.GetValue().strip() == '':
				message = str(obj['sender_id']) + ' '+ obj['message']
			else:
				message = self.outputText.GetValue()+'\n'+str(obj['sender_id']) + ' '+ obj['message']
			self.outputText.SetValue(message)


	def start(self):
		"""
		启动客户端
		"""
		self.__socket.connect(('127.0.0.1', 4444))
		# self.cmdloop()

	def do_login(self):
		"""
		登录聊天室
		:param args: 参数
		"""

		# 将昵称发送给服务器，获取用户id
		self.__socket.send(json.dumps({
			'type': 'login',
		}).encode())
		# 尝试接受数据
		# noinspection PyBroadException
		# try:
		buffer = self.__socket.recv(1024).decode()
		obj = json.loads(buffer)
		# if obj['sender_id']:
		self.__id = obj['id']
		print('[Client]'+str(self.__id)+' 成功登录到聊天室')

		# 开启子线程用于接受数据
		thread = threading.Thread(target=self.__receive_message_thread)
		thread.setDaemon(True)
		thread.start()
		# else:
		# 	print('[Client] 无法登录到聊天室')
		# except Exception:
		# 	print('[Client] 无法从服务器获取数据')

	def do_send(self, args):
		"""
		发送消息
		:param args: 参数
		"""
		message = args
		self.__socket.send(json.dumps({
			'type': 'broadcast',
			# 'sender_id': self.__id,
			'message': _des(str(self.__id)+':'+message,self.key.GetValue(),1)
		}).encode())

	def send(self,event):	#注意事件处理函数需要加上事件对象
		result = ''
		if self.__status:
			text = self.outputText.GetValue().split('\r')
			for t in text:
				if t.strip() != '':
					result = result + _des(t,self.key.GetValue(),self.__status) + '\n'
			self.outputText.SetValue(result)
			self.__status = 0
			self.encryptbtn.SetLabelText('decrypt')

		self.do_send(self.inputText.GetValue())
		
		# self.Close(True)	#强制退出force=True

	def encrypt(self,event):
		result = ''
		if self.__status:
			text = self.outputText.GetValue().split('\r')
			for t in text:
				if t.strip() != '':
					result = result + _des(t,self.key.GetValue(),self.__status) + '\n'
			self.outputText.SetValue(result)
			self.__status = 0
			self.encryptbtn.SetLabelText('decrypt')

		else:
			text = self.outputText.GetValue().split('\r')
			print(text)
			for t in text:
				if t.strip() != '':
					# if text.index(t) != len(text) - text.count('') - 1: #为了解密完回来少一个空行
					result = result + _des(t,self.key.GetValue(),self.__status) + '\n'
					# else:
						# result = result + _des(t,self.key.GetValue(),self.__status)
			self.outputText.SetValue(result)
			self.__status = 1
			self.encryptbtn.SetLabelText('encrypt')


class MyApp(wx.App):
	def OnInit(self):
		print("开始进入事件循环")
		self.frame = MyFrame(None)
		self.frame.Show(True)
		self.frame.GetId()
		return True #需要返回一个布尔型，只有初始返回成功，程序才会继续执行

	def OnExit(self):
		print("事件循环结束")
		import time
		time.sleep(2)
		return 0	#返回状态码




# class Client(Cmd):
# 	"""
# 	客户端
# 	"""
# 	prompt = ''
# 	intro = '[Welcome] 简易聊天室客户端(Cli版)\n' + '[Welcome] 输入help来获取帮助\n'

# 	def __init__(self):
# 		"""
# 		构造
# 		"""
# 		super().__init__()
# 		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 		self.__id = None
# 		self.__nickname = None

# 	def __receive_message_thread(self):
# 		"""
# 		接受消息线程
# 		"""
# 		while True:
# 			# noinspection PyBroadException
# 			try:
# 				buffer = self.__socket.recv(1024).decode()
# 				obj = json.loads(buffer)
# 				print('[' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + ']', obj['message'])
# 			except Exception:
# 				print('[Client] 无法从服务器获取数据')

# 	def __send_message_thread(self, message):
# 		"""
# 		发送消息线程
# 		:param message: 消息内容
# 		"""
# 		self.__socket.send(json.dumps({
# 			'type': 'broadcast',
# 			'sender_id': self.__id,
# 			'message': message
# 		}).encode())

# 	def start(self):
# 		"""
# 		启动客户端
# 		"""
# 		self.__socket.connect(('127.0.0.1', 4444))
# 		# self.cmdloop()

# 	def do_login(self, args):
# 		"""
# 		登录聊天室
# 		:param args: 参数
# 		"""
# 		nickname = args.split(' ')[0]

# 		# 将昵称发送给服务器，获取用户id
# 		self.__socket.send(json.dumps({
# 			'type': 'login',
# 			'nickname': nickname
# 		}).encode())
# 		# 尝试接受数据
# 		# noinspection PyBroadException
# 		try:
# 			buffer = self.__socket.recv(1024).decode()
# 			obj = json.loads(buffer)
# 			# if obj['id']:
# 			# 	self.__nickname = nickname
# 			# 	self.__id = obj['id']
# 			# 	print('[Client] 成功登录到聊天室')

# 				# 开启子线程用于接受数据
# 			thread = threading.Thread(target=self.__receive_message_thread)
# 			thread.setDaemon(True)
# 			thread.start()
# 			# else:
# 			# 	print('[Client] 无法登录到聊天室')
# 		except Exception:
# 			print('[Client] 无法从服务器获取数据')

# 	def do_send(self, args):
# 		"""
# 		发送消息
# 		:param args: 参数
# 		"""
# 		print(args)
# 		message = args
# 		# 显示自己发送的消息
# 		print('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']', message)
# 		# 开启子线程用于发送数据
# 		thread = threading.Thread(target=self.__send_message_thread, args=(message, ))
# 		thread.setDaemon(True)
# 		thread.start()

# 	def do_help(self, arg):
# 		"""
# 		帮助
# 		:param arg: 参数
# 		"""
# 		command = arg.split(' ')[0]
# 		if command == '':
# 			print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
# 			print('[Help] send message - 发送消息，message是你输入的消息')
# 		elif command == 'login':
# 			print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
# 		elif command == 'send':
# 			print('[Help] send message - 发送消息，message是你输入的消息')
# 		else:
# 			print('[Help] 没有查询到你想要了解的指令')
