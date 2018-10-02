import wx

class MyFrame(wx.Frame):    #创建自定义Frame
    def __init__(self,parent):
        #def __init__(
        # self, parent=None, id=None, title=None, pos=None,
        # size=None, style=None, name=None)

        wx.Frame.__init__(self,parent,id=-1,title="Hello World",size=(300,300),pos=(0,0)) #设置窗体

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)


        panel.SetSizer(sizer)

        txt = wx.StaticText(panel,-1,"Hello World!")    #创建静态文本组件
        sizer.Add(txt,0,wx.TOP|wx.LEFT,100)

        self.quitbtn = wx.Button(panel,-1,"Quit")
        self.sendbtn = wx.Button(panel,-1,"Quit")
        self.inputText = wx.TextCtrl(panel,-1,"",size=(150,-1))
        self.inputText.SetInsertionPoint(0) #设置焦点位置
        sizer.Add(self.inputText,100,100,100)
        sizer.Add(self.quitbtn,0,0,100)
        sizer.Add(self.sendbtn,0,0,100)

        # self.Bind(wx.EVT_BUTTON,self.OnClick,self.btn)
        # self.Bind(wx.EVT_ENTER_WINDOW,self.OnEnterWindow,self.btn)
        self.quitbtn.Bind(wx.EVT_BUTTON,self.OnClick)   #绑定鼠标进入事件
        self.Center()   #将窗口放在桌面环境的中间
   
    def OnClick(self,event):    #注意事件处理函数需要加上事件对象
        print("我被点击了")
        self.Close(True)    #强制退出force=True

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
        return 0    #返回状态码

app = MyApp()

app.MainLoop()

