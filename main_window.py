# coding:utf-8
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel,QSizePolicy,QFileDialog

from qfluentwidgets import (NavigationInterface, NavigationItemPosition,
                            isDarkTheme,setTheme,Theme,Dialog)
from qfluentwidgets import FluentIcon as FIF,ToolTipPosition,ToolTipFilter,SystemTrayMenu,MessageBox,Action,RoundMenu,InfoBar,InfoBarPosition,InfoBarIcon,TransparentToggleToolButton,FluentStyleSheet,ListWidget,TransparentPushButton
from qfluentwidgets.components.material import AcrylicComboBox
from qframelesswindow import FramelessWindow, StandardTitleBar,FramelessDialog
import XTC_box_ui
from config import cfg,MyFluentIcon


class FileSearchResWidget(FramelessDialog):
    closeSignal = pyqtSignal()
    addFileSignal = pyqtSignal(str)
    data = []

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.windowTitleLabel = QLabel('搜索中...', self)
        self.setResizeEnabled(False)
        self.resize(400, 450)
        self.windowTitleLabel.resize(self.width(),self.windowTitleLabel.height())

        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())
        self.setWindowModality(Qt.ApplicationModal)

        self.listWidget = ListWidget(parent=self)
        self.listWidget.setGeometry(0,self.windowTitleLabel.height(),self.width(),self.height()-self.windowTitleLabel.height()-60)

        self.closeButton = TransparentPushButton(parent=self)
        self.closeButton.setText('关闭')
        self.closeButton.setGeometry(self.width()//2-self.closeButton.width()//2,self.height()-50,100,40)
        self.closeButton.clicked.connect(lambda :(self.close(),self.closeSignal.emit()))

    def setTitleBarVisible(self, isVisible: bool):
        self.windowTitleLabel.setVisible(isVisible)

    def addFileFunc(self,path):
        self.listWidget.addItem(path)
        self.data.append(path)
# class SystemTrayIcon(QSystemTrayIcon):
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.setIcon(parent.windowIcon())
#         self.setToolTip('当前连接:无')
#         home=Action(FIF.HOME,'主页', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(0)))
#         app=RoundMenu('应用功能')
#         app.setIcon(FIF.APPLICATION)
#         app.addActions([
#             Action(FIF.DOWNLOAD,'安装应用', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(1))),
#             Action(FIF.APPLICATION,'应用管理', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(2))),
#             Action(FIF.MARKET,'进程管理', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(3))),
#             Action(MyFluentIcon.KEYBOARD,'输入法管理', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(4))),
#         ])
#         self.menu = SystemTrayMenu(parent=parent)
#         self.menu.addAction(home)
#         self.menu.addMenu(app)
#         self.func = RoundMenu("设备管理")
#         self.func.setIcon(FIF.DEVELOPER_TOOLS)
#         self.func.addActions([
#             Action(FIF.FIT_PAGE,"屏幕管理", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(5))),
#             Action(MyFluentIcon.BATTERY,"充电管理", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(6))),
#             Action(FIF.FOLDER,"文件管理", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(7))),
#             Action(FIF.COMMAND_PROMPT,"一键ROOT", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(8)))
#         ])
#         self.menu.addMenu(self.func)
#         self.menu.addAction(Action(FIF.SETTING,"设置",triggered=lambda:(self.parent().stackWidget.setCurrentIndex(9))))
#         self.setContextMenu(self.menu)
class Main_Title_Bar(StandardTitleBar):
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.parent=parent
        self.istop=False
        self.frame=QFrame(parent=self)
        self.frame.setObjectName('device_frame')
        self.hBoxLayout2=QHBoxLayout()
        self.label=QLabel(parent=self.frame)
        self.label.setText("选择设备:")
        self.combobox=AcrylicComboBox(parent=self.frame)
        self.hBoxLayout2.addWidget(self.label)
        self.hBoxLayout2.addWidget(self.combobox)
        self.frame.setLayout(self.hBoxLayout2)
        self.hBoxLayout2.setContentsMargins(0,0,0,0)
        self.hBoxLayout2.setSpacing(0)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.top_btn = TransparentToggleToolButton(parent=self)
        self.top_btn.setIcon(FIF.PIN)
        self.resize(100,100)
        self.top_btn.resize(50,self.height())
        self.top_btn.setObjectName('TopButton')
        self.top_btn.clicked.connect(self.to_top)
    def to_top(self):
        if not self.istop:
            self.istop=True
            self.parent.setWindowFlags(Qt.WindowStaysOnTopHint)
        else:
            self.istop=False
            self.parent.setWindowFlags(Qt.Widget)
        self.parent.show()
    def resizeEvent(self, e):
        w, h = self.width(), self.height()
        self.top_btn.move(self.width() - self.top_btn.width() - 138, 0)
        self.frame.resize(w // 4, self.frame.height())
        self.frame.move(w // 2 - self.frame.width() // 2, h // 2 - self.frame.height() // 2)


class Main_Window_Widget(FramelessWindow):
    resize_event=pyqtSignal(int,int)
    def __init__(self):
        super().__init__()
        self.title_bar=Main_Title_Bar(self)
        self.setTitleBar(self.title_bar)
        # self.systemTrayIcon = SystemTrayIcon(self)
        # self.systemTrayIcon.show()
        self.on_close = False
    def closeEvent(self, event):
        def goto(on:bool):
            if on:
                event.accept()
            else:
                event.ignore()
        if not self.on_close:
            m = Dialog(title='温馨提示:',
                           content='确定要退出小天才专用工具箱吗?[伤心]',
                           parent=self)
            m.yesButton.setText('是')
            m.cancelButton.setText('否')
            if not m.exec():
                event.ignore()
                return
            # self.systemTrayIcon.hide()

    def resizeEvent(self, e):
        self.resize_event.emit(self.width(),self.height())
        super().resizeEvent(e)

class AutoRootToolMain(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui = XTC_box_ui.AutoRootTool()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class Screen_Setting_Main(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui = XTC_box_ui.Screen_setting()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class File_List_Main(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui = XTC_box_ui.File_list_main()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class Input_List_Main(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui = XTC_box_ui.Input_list()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class Ps_List_Main(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui = XTC_box_ui.Ps_list()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class App_List_Main(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui = XTC_box_ui.App_List_Widget()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class Setting_Main(XTC_box_ui.SettingInterface):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.expandLayout.setContentsMargins(0,0,0,0)
        self.setObjectName(text.replace(' ', '-'))
class Home_Main(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui=XTC_box_ui.Home_Form()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class Apk_Install_Main(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.ui=XTC_box_ui.Apk_Install_Window()
        self.ui.setupUi(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

class Main_Window(Main_Window_Widget):
    message = pyqtSignal(str,str,str,str,str)
    choose_doc = pyqtSignal(str,str)
    show_info_singal = pyqtSignal(str, str)
    show_error_singal = pyqtSignal(str, str,int)
    setPath_signal = pyqtSignal(tuple)
    setFileName = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.show_info_singal.connect(self.show_info)
        self.show_error_singal.connect(self.show_error)
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)
        self.navigationInterface.setObjectName("navigationInterface")
        # create sub interface
        self.home = Home_Main('home_main', self)
        self.app_installer = Apk_Install_Main('app_installer', self)
        self.app_manager = App_List_Main('app_manager', self)
        self.pross_manager = Ps_List_Main('pross_manager', self)
        self.keyboard_manager = Input_List_Main('keyboard_manager', self)
        self.file_manager = File_List_Main('file_manager', self)
        self.settingInterface = Setting_Main('Setting Interface', self)
        self.screen_setting = Screen_Setting_Main('screen_setting', self)
        self.battery = Widget('battery', self)
        self.auto_root = AutoRootToolMain('auto_root', self)
        self.auto_start = Widget('auto_start',self)
        self.magisk = Widget('magisk',self)
        self.more = Widget('more',self)
        self.setFileName.connect(self.file_manager.ui.set_file_name)
        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)
    def showMessage(self,signalName,title,content,yesbtn,nobtn):
        self.signalInfo[signalName] = None
        m = MessageBox(title=title,
                       content=content,
                       parent=self)
        m.yesButton.setText(yesbtn)
        m.cancelButton.setText(nobtn)
        res = m.exec()
        self.signalInfo[signalName] = res
        return res
    def show_info(self,title,content):
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title=title,
            content=content,
            orient=Qt.Horizontal,  # vertical layout
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
        w.show()
    def show_error(self,title,content,place):
        if place==0:place=InfoBarPosition.TOP
        elif place==3:place=InfoBarPosition.TOP_RIGHT
        w = InfoBar(
            icon=InfoBarIcon.ERROR,
            title=title,
            content=content,
            orient=Qt.Horizontal,  # vertical layout
            isClosable=False,
            position=place, #TOP = 0,BOTTOM = 1,TOP_LEFT = 2,TOP_RIGHT = 3,BOTTOM_LEFT = 4,BOTTOM_RIGHT = 5,NONE = 6
            duration=2000,
            parent=self
        )
        w.show()
    def initNavigation(self):
        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.addSubInterface(self.home, FIF.HOME, '主页')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.app_installer, FIF.DOWNLOAD, '安装应用')
        self.addSubInterface(self.app_manager, FIF.APPLICATION, '应用管理')
        self.addSubInterface(self.pross_manager, FIF.MARKET, '进程管理')
        self.addSubInterface(self.keyboard_manager, MyFluentIcon.KEYBOARD, '输入法管理')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.screen_setting, FIF.FIT_PAGE, '屏幕设置')
        self.addSubInterface(self.battery, MyFluentIcon.BATTERY, '充电管理')
        self.addSubInterface(self.file_manager, FIF.FOLDER, '文件管理')
        self.addSubInterface(self.auto_root, FIF.COMMAND_PROMPT, 'root工具')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.auto_start, FIF.DEVELOPER_TOOLS, '自启动管理')
        self.addSubInterface(self.magisk,MyFluentIcon.MAGISK, 'magisk工具')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.more,FIF.MORE,'更多')

        # add custom widget to bottom
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        #!IMPORTANT: don't forget to set the default route key if you enable the return button
        # setDefaultRouteKey(self.stackWidget, self.musicInterface.objectName())

        # set the maximum width
        # self.navigationInterface.setExpandWidth(300)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)
        # always expand
        # self.navigationInterface.setCollapsible(False)

    def setHomeMainConnect(self):
        self.home.ui.PushButton.clicked.connect(lambda:(self.stackWidget.setCurrentIndex(1)))
        self.home.ui.PushButton_2.clicked.connect(lambda:(self.stackWidget.setCurrentIndex(2)))
        self.home.ui.PushButton_3.clicked.connect(lambda:(self.stackWidget.setCurrentIndex(3)))
        self.home.ui.PushButton_4.clicked.connect(lambda:(self.stackWidget.setCurrentIndex(4)))
        self.home.ui.PushButton_5.clicked.connect(lambda: (self.stackWidget.setCurrentIndex(5)))
        self.home.ui.PushButton_6.clicked.connect(lambda: (self.stackWidget.setCurrentIndex(6)))
        self.home.ui.PushButton_7.clicked.connect(lambda: (self.stackWidget.setCurrentIndex(7)))
        self.home.ui.PushButton_8.clicked.connect(lambda: (self.stackWidget.setCurrentIndex(8)))
        self.home.ui.PushButton_6.setIcon(MyFluentIcon.BATTERY)
        self.home.ui.PushButton_4.setIcon(MyFluentIcon.KEYBOARD)
        self.home.ui.PushButton.setToolTip("提供各种应用安装的方式")
        self.home.ui.PushButton.setToolTipDuration(2000)
        self.home.ui.PushButton.installEventFilter(ToolTipFilter(self.home.ui.PushButton, 300, ToolTipPosition.TOP))
        self.home.ui.PushButton_2.setToolTip("快速解析、启动、冻结、卸载、管理应用")
        self.home.ui.PushButton_2.setToolTipDuration(2000)
        self.home.ui.PushButton_2.installEventFilter(ToolTipFilter(self.home.ui.PushButton_2, 300, ToolTipPosition.TOP))
        self.home.ui.PushButton_3.setToolTip("快速解析、关闭、冻结、管理进程")
        self.home.ui.PushButton_3.setToolTipDuration(2000)
        self.home.ui.PushButton_3.installEventFilter(ToolTipFilter(self.home.ui.PushButton_3, 300, ToolTipPosition.BOTTOM))
        self.home.ui.PushButton_4.setToolTip("快速解析、启用、管理输入法")
        self.home.ui.PushButton_4.setToolTipDuration(2000)
        self.home.ui.PushButton_4.installEventFilter(ToolTipFilter(self.home.ui.PushButton_4, 300, ToolTipPosition.BOTTOM))
        self.home.ui.PushButton_5.setToolTip("设置屏幕DPI和大小、深/浅色主题、一件截图、投屏")
        self.home.ui.PushButton_5.setToolTipDuration(2000)
        self.home.ui.PushButton_5.installEventFilter(ToolTipFilter(self.home.ui.PushButton_5, 300, ToolTipPosition.TOP))
        self.home.ui.PushButton_6.setToolTip("设置电池电量、充电方式")
        self.home.ui.PushButton_6.setToolTipDuration(2000)
        self.home.ui.PushButton_6.installEventFilter(ToolTipFilter(self.home.ui.PushButton_6, 300, ToolTipPosition.TOP))
        self.home.ui.PushButton_7.setToolTip("特别好用的桌面式图形化文件管理器")
        self.home.ui.PushButton_7.setToolTipDuration(2000)
        self.home.ui.PushButton_7.installEventFilter(ToolTipFilter(self.home.ui.PushButton_7, 300, ToolTipPosition.BOTTOM))
        self.home.ui.PushButton_8.setToolTip("一键ROOT、恢复原样(有风险)")
        self.home.ui.PushButton_8.setToolTipDuration(2000)
        self.home.ui.PushButton_8.installEventFilter(ToolTipFilter(self.home.ui.PushButton_8, 300, ToolTipPosition.BOTTOM))
        self.home.ui.magiskToolButton.setIcon(MyFluentIcon.MAGISK)
    def initWindow(self):
        self.signalInfo = dict()
        self.resize(900, 700)
        self.setWindowFlags(Qt.Widget)
        self.setWindowIcon(QIcon('./img/ico.png'))
        self.setWindowTitle('小天才专用工具箱')
        self.setHomeMainConnect()
        self.message.connect(self.showMessage)
        self.navigationInterface.setCurrentItem("home_main")
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        cfg.themeChanged.connect(lambda theme:(self.setQss(theme),self.settingInterface.onThemeChanged(theme)))
        self.setQss(cfg.themeMode.value)
        self.setPath_signal.connect(self.file_manager.ui.setPath)
    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )
    def show_choose_doc(self,title,doc):
        path=QFileDialog.getExistingDirectory(parent=self,caption=title,directory=doc)
        return path
    def setQss(self,theme:Theme):
        setTheme(theme)
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'style/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        if isDarkTheme():self.home.setStyleSheet(".QWidget{background-color:rgb(32, 32, 32)}")
        else:self.home.setStyleSheet(".QWidget{background-color:white}")
    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

        #!IMPORTANT: This line of code needs to be uncommented if the return button is enabled
        # qrouter.push(self.stackWidget, widget.objectName())
