# coding:utf-8
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel,QSystemTrayIcon,QSizePolicy,QFileDialog

from qfluentwidgets import (NavigationInterface, NavigationItemPosition,
                            isDarkTheme,setTheme,Theme)
from qfluentwidgets import FluentIcon as FIF,FluentIconBase,getIconColor,ToolTipPosition,ToolTipFilter,SystemTrayMenu,MessageBox,Action,RoundMenu,ComboBox,InfoBar,InfoBarPosition,InfoBarIcon
from qframelesswindow import FramelessWindow, StandardTitleBar
import XTC_box_ui # 界面
from enum import Enum
from config import cfg

class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(parent.windowIcon())
        self.setToolTip('当前连接:无')
        home=Action('主页', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(0)))
        home.setIcon(FIF.HOME)
        app=RoundMenu('应用功能')
        app.setIcon(FIF.APPLICATION)
        app.addActions([
            Action(FIF.DOWNLOAD,'安装应用', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(1))),
            Action(FIF.APPLICATION,'应用管理', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(2))),
            Action(FIF.MARKET,'进程管理', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(3))),
            Action(MyFluentIcon.KEYBOARD,'输入法管理', triggered=lambda:(self.parent().stackWidget.setCurrentIndex(4))),
        ])
        self.menu = SystemTrayMenu(parent=parent)
        self.menu.addAction(home)
        self.menu.addMenu(app)
        self.func = RoundMenu("设备管理")
        self.func.setIcon(FIF.DEVELOPER_TOOLS)
        self.func.addActions([
            Action(FIF.FIT_PAGE,"屏幕管理", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(5))),
            Action(MyFluentIcon.BATTERY,"充电管理", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(6))),
            Action(FIF.FOLDER,"文件管理", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(7))),
            Action(FIF.COMMAND_PROMPT,"一键ROOT", triggered=lambda:(self.parent().stackWidget.setCurrentIndex(8)))
        ])
        self.menu.addMenu(self.func)
        self.menu.addAction(Action(FIF.SETTING,"设置",triggered=lambda:(self.parent().stackWidget.setCurrentIndex(9))))
        self.setContextMenu(self.menu)
class Main_Title_Bar(StandardTitleBar):
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.frame=QFrame(parent=self)
        self.frame.setObjectName('device_frame')
        self.hBoxLayout2=QHBoxLayout()
        self.label=QLabel(parent=self.frame)
        self.label.setText("选择设备:")
        self.combobox=ComboBox(parent=self.frame)
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
    def resizeEvent(self, e):
        w, h = self.width(), self.height()
        self.frame.resize(w // 4, self.frame.height())
        self.frame.move(w // 2 - self.frame.width() // 2, h // 2 - self.frame.height() // 2)


class Main_Window_Widget(FramelessWindow):
    resize_event=pyqtSignal(int,int)
    def __init__(self):
        super().__init__()
        self.title_bar=Main_Title_Bar(self)
        self.setTitleBar(self.title_bar)
        self.on_close = False
    def closeEvent(self, event):
        if not self.on_close:
            m = MessageBox(title='温馨提示:',
                           content='确定要推出吗?',
                           parent=self)
            m.yesButton.setText('是')
            m.cancelButton.setText('否')
            if not m.exec():
                event.ignore()

    def resizeEvent(self, e):
        self.resize_event.emit(self.width(),self.height())
        super().resizeEvent(e)

class MyFluentIcon(FluentIconBase, Enum):
    """ Custom icons """

    BATTERY = "battery"
    KEYBOARD = "keyboard"

    def path(self, theme=Theme.AUTO):
        return f'./img/{self.value}_{getIconColor(theme)}.png'

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
    message = pyqtSignal(str,str,str,str)
    choose_doc = pyqtSignal(str,str)
    show_info_singal = pyqtSignal(str, str)
    show_error_singal = pyqtSignal(str, str)
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
        self.file_manaer = Widget('file_manager', self)
        self.settingInterface = Setting_Main('Setting Interface', self)
        self.screen_setting = Widget('screen_setting', self)
        self.battery = Widget('battery', self)
        self.auto_root = Widget('auto_root', self)

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
    def showMessage(self,title:str,content:str,yesbtn:str,nobtn:str):
        m = MessageBox(title=title,
                       content=content,
                       parent=self)
        m.yesButton.setText(yesbtn)
        m.cancelButton.setText(nobtn)
        m.exec()
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
    def show_error(self,title,content):
        w = InfoBar(
            icon=InfoBarIcon.ERROR,
            title=title,
            content=content,
            orient=Qt.Horizontal,  # vertical layout
            isClosable=False,
            position=InfoBarPosition.TOP,
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
        self.addSubInterface(self.file_manaer, FIF.FOLDER, '文件管理')
        self.addSubInterface(self.auto_root, FIF.COMMAND_PROMPT, 'root工具')

        # add custom widget to bottom
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        #!IMPORTANT: don't forget to set the default route key if you enable the return button
        # qrouter.setDefaultRouteKey(self.stackWidget, self.musicInterface.objectName())

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
        self.home.ui.PushButton_6.setToolTip("设置电池点亮、充电方式")
        self.home.ui.PushButton_6.setToolTipDuration(2000)
        self.home.ui.PushButton_6.installEventFilter(ToolTipFilter(self.home.ui.PushButton_6, 300, ToolTipPosition.TOP))
        self.home.ui.PushButton_7.setToolTip("特别好用的桌面式图形化文件管理器")
        self.home.ui.PushButton_7.setToolTipDuration(2000)
        self.home.ui.PushButton_7.installEventFilter(ToolTipFilter(self.home.ui.PushButton_7, 300, ToolTipPosition.BOTTOM))
        self.home.ui.PushButton_8.setToolTip("一键ROOT、恢复原样(有风险)")
        self.home.ui.PushButton_8.setToolTipDuration(2000)
        self.home.ui.PushButton_8.installEventFilter(ToolTipFilter(self.home.ui.PushButton_8, 300, ToolTipPosition.BOTTOM))
    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('./img/ico.png'))
        self.setWindowTitle('小天才专用工具箱')
        self.setHomeMainConnect()
        self.message.connect(self.showMessage)
        self.navigationInterface.setCurrentItem("home_main")
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.systemTrayIcon = SystemTrayIcon(self)
        self.systemTrayIcon.show()
        cfg.themeChanged.connect(lambda theme:(self.setQss(theme),self.settingInterface.onThemeChanged(theme)))
        self.setQss(cfg.themeMode.value)

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
