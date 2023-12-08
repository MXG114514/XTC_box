# coding:utf-8
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator)


class Config(QConfig):
    """ Config of application """
    a=ConfigItem('adb','shell',False,BoolValidator())
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


YEAR = 2023
AUTHOR = "MXG"
VERSION = "0.3"
HELP_URL = "https://www.bilibili.com/video/BV1hq4y1s7VH/?spm_id_from=333.337.search-card.all.click"
FEEDBACK_URL = "https://space.bilibili.com/3461574094228294?spm_id_from=333.1007.0.0"
RELEASE_URL = "https://www.bilibili.com/video/BV1hq4y1s7VH/?spm_id_from=333.337.search-card.all.click"


cfg = Config()
qconfig.load('./config/config.json', cfg)