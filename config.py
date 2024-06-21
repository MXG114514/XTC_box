# coding:utf-8
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator)
from qfluentwidgets import FluentIconBase,Theme,getIconColor
from enum import Enum

class Config(QConfig):
    """ Config of application """
    # main window
    enableAcrylicBackground = ConfigItem(
        "MainWindow", "EnableAcrylicBackground", False, BoolValidator())
    minimizeToTray = ConfigItem(
        "MainWindow", "MinimizeToTray", True, BoolValidator())
    playBarColor = ColorConfigItem("MainWindow", "PlayBarColor", "#225C7F")
    recentPlaysNumber = RangeConfigItem(
        "MainWindow", "RecentPlayNumbers", 300, RangeValidator(10, 300))
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    # software update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", False, BoolValidator())

class MyFluentIcon(FluentIconBase, Enum):
    """ Custom icons """

    MAGISK = 'magisk'
    BATTERY = "battery"
    KEYBOARD = "keyboard"
    TXT = 'txt'
    ZIP = 'zip'
    APK = 'apk'

    def path(self, theme=Theme.AUTO):
        return f'./img/{self.value}_{getIconColor(theme)}.png'

YEAR = 2024
AUTHOR = "MXG"
VERSION = "0.6"
HELP_URL = "https://www.bilibili.com/video/BV1hq4y1s7VH/?spm_id_from=333.337.search-card.all.click"
FEEDBACK_URL = "https://space.bilibili.com/3461574094228294?spm_id_from=333.1007.0.0"
RELEASE_URL = "https://www.bilibili.com/video/BV1hq4y1s7VH/?spm_id_from=333.337.search-card.all.click"


cfg = Config()
qconfig.load('./config/config.json', cfg)