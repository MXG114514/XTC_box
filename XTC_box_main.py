from sys import argv,exit
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QDesktopServices
from config import cfg,VERSION
from XTC_box_ui import Welcome_Window,InputMessageBox
from main_window import Main_Window,FileSearchResWidget
from subprocess import run,PIPE,Popen
from re import compile,findall,S
from threading import Thread,RLock,Event
from qfluentwidgets import InfoBar,InfoBarPosition,InfoBarIcon,MessageBox,FluentTranslator,StateToolTip,PushButton
from os import environ,path,stat
from requests import get
from datetime import datetime
from zipfile import ZipFile
from ctypes import windll
from time import sleep


windll.shell32.SetCurrentProcessExplicitAppUserModelID("XTC_box")
desktop_path = path.join(path.expanduser("~"), 'Desktop')
class New_StateToolTip(StateToolTip):
    def __init__(self,parent=None,**kargs):
        super().__init__(parent=parent,**kargs)
        self.parent=parent
        self.move(self.parent.width()-self.width()-20,35)
        main_window.resize_event.connect(self.resize_singal)
    def resize_singal(self,w,h):
        self.move(w-self.width()-20,35)
    def resizeEvent(self, a0) -> None:
        self.move(self.parent.width() - self.width() - 20,35)
        super().resizeEvent(a0)
class XTC_func():
    def __init__(self):
        self.sdk={"1":"Android 1.0","2":"Android 1.1","3":"Android 1.5","4":"Android 1.6","5":"Android 2.0","6":"Android 2.0.1","7":"Android 2.1.x","8":"Android 2.2.x","9":"Android 2.3.2 Android 2.3.1 Android 2.3","10":"Android 2.3.4 Android 2.3.3","11":"Android 3.0.x","12":"Android 3.1.x","13":"Android 3.2","14":"Android 4.0、4.0.1、4.0.2","15":"Android 4.0.3、4.0.4","16":"Android 4.1、4.1.1","17":"Android 4.2、4.2.2","18":"Android 4.3","19":"Android 4.4","20":"Android 4.4W","21":"Android 5.0","22":"Android 5.1","23":"Android 6.0","24":"Android 7.0","25":"Android 7.1.1","26":"Android 8.0","27":"Android 8.1","28":"Android 9.0","29":"Android 10.0","30":"Android 11","31":"Android 12","32":"Android 12","33":"Android 13"}
        self.info={"size":["--","--"],"dpi":["--","--"],"sdcard":["--","--"],"root":["--","--"],"battery":"--","version":"--","name":"--","model":"--","is_root":"--","brand":"--",'ps':{},'keyboard':{}}
    def show_no_device_error(self):
        main_window.show_error_singal.emit('操作错误', '未连接设备',0)
        return
    def get_device(self):
        return main_window.title_bar.combobox.currentText()
    def saveAutoStartXML(self):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
            return
        main_window.show_info_singal.emit('等待重启...','')
        run_cmd(f'adb -s {device} push ../temp/watch_boot_start.xml /data/data/com.xtc.i3launcher/shared_prefs/watch_boot_start.xml & adb -s {device} push ../temp/watch_boot_start_ex.xml /data/data/com.xtc.i3launcher/shared_prefs/watch_boot_start_ex.xml & adb -s {device} shell reboot')
        main_window.show_info_singal.emit('等待开机...','')
        run_cmd(f'adb -s {device} am start -n com.xtc.setting.module.appmanage.view.WatchBootStart')
        main_window.show_info_singal.emit('请打开手表','在手表中激活添加的应用')
        main_window.show_info_singal.emit('操作完成后再次重启...','')
    def getAutoStartXML(self):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
            return
        res = run_cmd(
            f'adb -s {device} pull /data/data/com.xtc.i3launcher/shared_prefs/watch_boot_start.xml ../temp/watch_boot_start.xml & adb pull /data/data/com.xtc.i3launcher/shared_prefs/watch_boot_start_ex.xml ../temp/watch_boot_start_ex.xml')
        res = run_cmd(
            f'adb -s {device} pull /data/data/com.xtc.i3launcher/shared_prefs/watch_boot_start.xml ../temp/watch_boot_start.xml.bak & adb pull /data/data/com.xtc.i3launcher/shared_prefs/watch_boot_start_ex.xml ../temp/watch_boot_start_ex.xml.bak')
    def setAutoStart(self,package:str,state:bool):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
            return
        xml1 = open('./temp/watch_boot_start.xml',mode='r')
        line = 1
        k=0
        info = xml1.read()
        if '</map>' not in info:
            return
        info = info.split('\n')
        for i in info:
            if '</map>' in i:
                break
            else:
                line+=1
        info.insert(line-1,f'    <boolean name="{package}" value="{"true" if state else "false"}" />')
        xml1.close()
        xml1 = open('./temp/watch_boot_start.xml',mode='w+')
        xml1.write('\n'.join(info))
        xml1.close()
        xml2 = open('./temp/watch_boot_start_ex.xml', mode='r')
        line = 1
        info = xml2.read()
        if '</map>' not in info:
            return
        info = info.split('\n')
        for i in info:
            if '</map>' in i:
                break
            else:
                line += 1
        info.insert(line - 1, f'    <int name="{package}" value="{"1" if state else "0"}" />')
        xml2.close()
        xml2 = open('./temp/watch_boot_start_ex.xml', mode='w+')
        xml2.write('\n'.join(info))
        xml2.close()
        main_window.show_info_singal.emit('操作完成!','')
    def rootBack(self,insertFunc):
        if self.get_device() == '':
            self.show_no_device_error()
            return
        data_inserter(insertFunc, (1, '回刷root时请尽量保持单一设备连接\n'))
        data_inserter(insertFunc, (1, '设备即将进入9008模式,请不要对手表和电脑进行任何操作!\n'))
        sleep(5)
        data_inserter(insertFunc, (1, '正在向设备发送进入9008命令...'))
        res = run_cmd('adb wait-for-device shell reboot edl')
        sleep(2)
        if res[0]:
            data_inserter(insertFunc, (1, '完成!\n'))
        else:
            data_inserter(insertFunc, (0, '失败,请重试!\n'))
            data_inserter(insertFunc, (0, f'输出:{res[1] if res[1] != "" else "Null"}'))
            data_inserter(insertFunc, (0, '操作失败\n'))
            return 0
        data_inserter(insertFunc, (1, '正在搜索9008端口...'))
        port = []
        while port == []:
            res = run_cmd('lsusb')
            port = findall(r"Qualcomm HS-USB QDLoader 9008 \((?P<com>.*?)\)", res[1])
        if len(port) > 1:
            data_inserter(insertFunc, (0, '\n检测到多个9008端口,请保持单一设备连接后再重试!\n'))
            data_inserter(insertFunc, (0, '操作失败\n'))
            return 0
        elif len(port) == 0:
            data_inserter(insertFunc, (0, '\n未检测到9008端口,请检查设备连接!\n'))
            data_inserter(insertFunc, (0, '操作失败\n'))
            return 0
        port = port[0]
        data_inserter(insertFunc, (1, '完成!\n'))
        data_inserter(insertFunc, (1, f'检测到端口为:{port}'))
        data_inserter(insertFunc, (1, '准备回刷...'))
        res = run_cmd(
            f"QSaharaServer -s 13:framework\prog_emmc_firehose_8937_ddr_hisen.mbn -p \\\\.\\{port} | lolcat")
        print(res)
        data_inserter(insertFunc, (1, '启动QSaharaServer...'))
        data_inserter(insertFunc, (1, res[1]))
        data_inserter(insertFunc, (1, '如果启动QSaharaServer后提示error可无视,以程序检测的Magisk安装结果为准'))
        data_inserter(insertFunc, (1, '开始刷入分区...'))
        res = run_cmd(
            f'fh_loader.exe --port=\\\\.\\{port} --sendxml=./framework/back.xml --search_path={path.abspath("./adb/framework/")} --noprompt --showpercentagecomplete --memoryname=eMMC --setactivepartition=0 --reset > null')
        data_inserter(insertFunc, (1, res[1]))
        data_inserter(insertFunc,(1,'操作完成'))
    def autoRoot(self,mode,insertFunc):
        if self.get_device() == '':
            self.show_no_device_error()
            return 0
        if not mode:
            main_window.show_error_singal.emit('请选择机型!','','0')
            return
        modelName = {'Z8少年版':'Z8_SNB','Z8':'Z8','Z7':'Z7','Z7A':'Z7A','Z6巅峰版':'Z6_DFB','Z8A':'Z8A',}
        data_inserter(insertFunc,(1,'声明:\n本工具的root方案全部由Sky iMoo Team提供\n仅适用于高版本手表的旧版系统固件,使用前先使用超级恢复降级\n作者不对设备损坏负责\n'))
        sleep(5)
        data_inserter(insertFunc,(1,'请确认您的手表符合以下版本要求(真实版本):\n(1)Z6巅峰版-2.3.0\n(2)Z7-2.0.0\n(3)Z7-1.7.2\n(4)Z7A-1.4.0\n(5)Z8(少年版)-2.2.1\n'))
        sleep(5)
        main_window.message.emit('device_ver_check','版本检查',f'你的手表型号:{mode}是否符合:(1)Z6巅峰版-2.3.0 (2)Z7-2.0.0 (3)Z7-1.7.2 (4)Z7A-1.4.0 (5)Z8(少年版)-2.2.1','符合','不符合')
        while 1:
            sleep(0.3)
            try:
                if main_window.signalInfo['device_ver_check'] != None:
                    if not main_window.signalInfo['device_ver_check']:
                        data_inserter(insertFunc,(0,'操作中断!'))
                        return 0
                    else:break
            except:continue
        data_inserter(insertFunc,(1,'刷入root时请尽量保持单一设备连接\n'))
        data_inserter(insertFunc,(1,'设备即将进入9008模式,请不要对手表和电脑进行任何操作!\n'))
        sleep(5)
        data_inserter(insertFunc,(1,'正在向设备发送进入9008命令...'))
        res=run_cmd('adb wait-for-device shell reboot edl')
        sleep(2)
        if res[0]:data_inserter(insertFunc,(1,'完成!\n'))
        else:
            data_inserter(insertFunc,(0,'失败,请重试!\n'))
            data_inserter(insertFunc,(0,f'输出:{res[1] if res[1]!="" else "Null"}'))
            data_inserter(insertFunc, (0, 'root失败\n'))
            return 0
        data_inserter(insertFunc,(1,'正在搜索9008端口...'))
        port = []
        while port == []:
            res=run_cmd('lsusb')
            port = findall(r"Qualcomm HS-USB QDLoader 9008 \((?P<com>.*?)\)", res[1])
        if len(port) > 1:
            data_inserter(insertFunc,(0,'\n检测到多个9008端口,请保持单一设备连接后再重试!\n'))
            data_inserter(insertFunc, (0, 'root失败\n'))
            return 0
        elif len(port) == 0:
            data_inserter(insertFunc,(0,'\n未检测到9008端口,请检查设备连接!\n'))
            data_inserter(insertFunc, (0, 'root失败\n'))
            return 0
        port = port[0]
        data_inserter(insertFunc,(1,'完成!\n'))
        data_inserter(insertFunc,(1,f'检测到端口为:{port}'))
        data_inserter(insertFunc,(1,'准备刷入root...'))
        res = run_cmd(f"QSaharaServer -s 13:framework\prog_emmc_firehose_8937_ddr_hisen.mbn -p \\\\.\\{port} | lolcat")
        data_inserter(insertFunc,(1,'启动QSaharaServer...'))
        data_inserter(insertFunc,(1,res[1]))
        data_inserter(insertFunc,(1,'如果启动QSaharaServer后提示error可无视,以程序检测的Magisk安装结果为准'))
        data_inserter(insertFunc,(1,'开始刷入分区...'))
        print(f'fh_loader.exe --port=\\\\.\\{port} --sendxml=./framework/{modelName[mode]}.xml --search_path="{path.abspath("./adb/framework/")}" --noprompt --showpercentagecomplete --memoryname=eMMC --setactivepartition=0 --reset > null')
        res = run_cmd(f'fh_loader.exe --port=\\\\.\\{port} --sendxml=./framework/{modelName[mode]}.xml --search_path="{path.abspath("./adb/framework/")}" --noprompt --showpercentagecomplete --memoryname=eMMC --setactivepartition=0 --reset > null')
        data_inserter(insertFunc,(1,res[1]))
        data_inserter(insertFunc,(1,'刷入完成,开始检测magisk状态...'))
        res = run_cmd('adb wait-for-device shell magisk -v')
        if '23.0:MAGISK' not in res[1]:
            data_inserter(insertFunc,(0,'未成功安装magisk,请重试或手动刷入!'))
            data_inserter(insertFunc, (0, 'root失败\n'))
            return 0
        data_inserter(insertFunc,(1,'magisk安装成功!'))
        data_inserter(insertFunc,(1,'等待手表开机...'))
        data_inserter(insertFunc,(1,'等待手表一段时间...'))
        sleep(55)
        if mode == 'Z6_DFB':
            res = run_cmd('adb wait-for-device install -r ./framework/dfb.apk')
        else:
            res = run_cmd('adb wait-for-device install -r ./framework/magisk.apk')
        print(res)
        run_cmd('adb wait-for-device shell wm density 200')
        data_inserter(insertFunc,(1,'断开手表连接后打开magisk,设置自动响应-允许，超级用户通知-无以后重新将手表连接至电脑...'))
        main_window.show_info_singal.emit('操作','断开手表连接后打开magisk,设置自动响应-允许，超级用户通知-无以后重新将手表连接至电脑')
        sleep(30)
        run_cmd('adb wait-for-device shell wm density 320')
        data_inserter(insertFunc,(1,'开始修复magisk...'))
        run_cmd('adb wait-for-device push ./framework/xtcmodule.zip /sdcard/')
        run_cmd('adb wait-for-device shell \'su -c rm -R /data/adb/magisk/\'')
        res=run_cmd('adb wait-for-device push ./framework/magisk/ /sdcard/magisk/')
        print(res)
        res=run_cmd('adb wait-for-device shell su -c \'cp -R /sdcard/magisk /data/adb/\'')
        print(res)
        run_cmd('adb wait-for-device shell su -c \'chmod 777 -R /data/adb/magisk/\'')
        run_cmd('adb wait-for-device shell su -c \'chmod 777 -R /data/adb/magisk/*\'')
        data_inserter(insertFunc,(1,'修复完成!即将重启...'))
        run_cmd('adb wait-for-device reboot')
        run_cmd('adb wait-for-device')
        data_inserter(insertFunc, (1, '等待手表启动完成...'))
        sleep(20)
        data_inserter(insertFunc,(1,'开始刷入小天才基础模块...'))
        res=run_cmd('adb wait-for-device shell "su -c magisk --install-module /sdcard/xtcmodule.zip"')
        data_inserter(insertFunc,(1,res[1]))
        data_inserter(insertFunc,(1,'刷入完成!即将重启...'))
        run_cmd('adb wait-for-device')
        data_inserter(insertFunc,(1,'开始检查模块是否成功刷入...'))
        res=run_cmd('adb wait-for-device shell getprop ro.build.type')
        if res[1] == 'userdebug':
            data_inserter(insertFunc,(1,'刷入成功!'))
            data_inserter(insertFunc,(1,'root完成!'))
            return 1
        else:
            data_inserter(insertFunc,(0,'模块未刷入!请尝试手动刷入'))
            data_inserter(insertFunc, (0, 'root失败\n'))
            return 0
    def animationScale(self,speed:list):
        device = self.get_device()
        if device == '':
            if speed != []:
                self.show_no_device_error()
            return 0
        if speed != []:
            if speed[0]:run_cmd(f'adb -s {device} shell settings put global window_animation_scale {speed[0]}')
            if speed[1]:run_cmd(f'adb -s {device} shell settings put global transition_animation_scale {speed[1]}')
            if speed[2]:run_cmd(f'adb -s {device} shell settings put global animator_duration_scale {speed[2]}')
            main_window.show_info_singal.emit('设置成功','')
        else:
            res = run_cmd(f'adb -s {device} shell settings get global window_animation_scale & adb -s {device} shell settings get global transition_animation_scale & adb -s {device} shell settings get global animator_duration_scale')
            window,transition,animator = str(res[1]).split('\n')
            window = window if window != 'null' else '1'
            transition = transition if transition != 'null' else '1'
            animator = animator if animator != 'null' else '1'
            return window,transition,animator
    def setScreenRotation(self,mode):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
            return 0
        res = run_cmd(f'adb -s {device} shell content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:{mode}')
        main_window.show_info_singal.emit('设置成功', '')
    def setTheme(self,theme):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
            return 0
        res = run_cmd(f'adb -s {device} shell settings put secure ui_night_mode {theme}')
        main_window.show_info_singal.emit('设置成功','')
    def screenOffTimeOut(self,timeout = None):
        device = self.get_device()
        if timeout == None:
            if not device:
                return
            res=run_cmd(f'adb -s {device} shell settings get system screen_off_timeout')
            return res[1]
        else:
            if not device:
                self.show_no_device_error()
                return
            res=run_cmd(f'adb -s {device} shell settings set system screen_off_timeout {timeout}')
            return str(timeout)

    def screenShot(self,savePath):
        device = self.get_device()
        if not device:
            self.show_no_device_error()
            return
        time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        run_cmd(f'adb -s {device} shell screencap -p /sdcard/screenshot{time_now}.png')
        self.pull_file(save_path=savePath,file_path=f'/sdcard/',name=f'screenshot{time_now}.png')
        self.delete_file(path=f'/sdcard/screenshot{time_now}.png')
        main_window.show_info_singal.emit('截图成功!',f'截图保存在: {savePath}\screenshot{time_now}.png')
    def scrcpy(self,record=False,savePath=''):
        device = self.get_device()
        if not device:
            self.show_no_device_error()
            return
        main_window.show_info_singal.emit('开始投屏','')
        if not record:
            run_cmd(f'scrcpy -s {device}')
            main_window.show_info_singal.emit('投屏结束', '')
        else:
            time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            run_cmd(f'scrcpy -s {device} --record {savePath}屏幕录像{time_now}.mp4')
            main_window.show_info_singal.emit(f'投屏结束','视频保存在: {savePath}屏幕录像{time_now}.mp4')

    def find_file(self,cwd='/sdcard/', key='',widget=None):
        def start():
            data = {}
            path = cwd
            if self.info['is_root'] == '已开启':
                p = Popen(f'adb shell su -c \"ls -R {cwd} | grep {key}\"', shell=True, stdout=PIPE, stderr=PIPE, cwd='./adb/',
                          encoding='utf-8')
            else:
                p = Popen(f'adb shell ls -R {cwd} | grep {key}', shell=True, stdout=PIPE, stderr=PIPE,
                          cwd='./adb/',
                          encoding='utf-8')
            main_window.file_manager.ui.file_list.clear()
            while p.poll() is None:
                line = p.stdout.readline()
                line = line.strip()
                if line:
                    if '/' not in line:
                        data[line] = path
                        widget.addFileSignal.emit(path+line)
                    else:
                        path = line[0:-1] + '/'
        Thread(target=start).start()
    def get_file_info(self,file_path,type):
        device = self.get_device()
        res = run(args=["adb", "-s", device, "shell", "du", "-k",
                        file_path.replace("(", "\\(").replace(")", "\\)").replace(" ", r"\ ")], cwd="./adb/",
                  stdout=PIPE,
                  stderr=PIPE, shell=True)
        a = str(res.stdout, encoding="utf-8").split("\t")[0]
        if type in ["doc", "link"]:
            file = "/" + "/".join(file_path.split("/")[:-2])
            res = run(args=["adb", "-s", device, "shell", "ls", "-l",
                            file.replace("(", "\\(").replace(")", "\\)").replace(" ", r"\ ")], cwd="./adb/",
                      stdout=PIPE,
                      stderr=PIPE, shell=True)
            b = str(res.stdout, encoding="utf-8")
            c = []
            for i in b.split("\n")[1:-1]:
                if i.split("->")[0].split()[-1] == file_path.split("/")[-2]:
                    c =  i.split("->")[0].split()[5:7]
            return a, " ".join(c)
        else:
            file = file_path
            res = run(args=["adb", "-s", device, "shell", "ls", "-l",
                            file.replace("(", "\\(").replace(")", "\\)").replace(" ", r"\ ")], cwd="./adb/",
                      stdout=PIPE,
                      stderr=PIPE, shell=True)
            b = str(res.stdout, encoding="utf-8")
            c = b.split("->")[0].split()[5:7]
            return a, " ".join(c)
    def paste_file(self,old_path,new_path,mode = 'copy'):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
        old_path = old_path.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        new_path = new_path.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        if mode == 'copy':
            if self.info['is_root'] != '已开启':
                res = run_cmd(['adb','-s',device,'shell','cp',old_path,new_path])
            else:
                res = run_cmd(f'adb -s {device} shell su -c \'cp {old_path} {new_path}\'')
        else:
            if self.info['is_root'] != '已开启':
                res = run_cmd(['adb','-s',device,'shell','mv',old_path,new_path])
            else:
                res = run_cmd(f'adb -s {device} shell su -c \'mv {old_path} {new_path}\'')
        if res[0]:
            return 1
        else:
            return 0
    def new_doc(self,path,name):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
        path = path.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        name = name.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        if self.info['is_root'] != '已开启':
            res = run_cmd(['adb','-s',device,'shell','mkdir',path+name])
        else:
            res = run_cmd(f'adb -s {device} shell su -c \'mkdir {path+name}\'')
        if res[0]:
            main_window.show_info_singal.emit('创建成功','')
            return 1
        else:
            main_window.show_error_singal.emit('创建失败','',0)
            return 0
    def rename_file(self,file_path,old_name,new_name):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
        file_path = file_path.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        old_name = old_name.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        new_name = new_name.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        if self.info['is_root'] != '已开启':
            res = run_cmd('adb -s'+device+'shell mv'+file_path+old_name+' '+file_path+new_name)
        else:
            res = run_cmd(f'adb -s {device} shell su -c \'mv {file_path+old_name} {file_path+new_name}\'')
        if res[0]:
            return 1
        else:
            return 0
    def push_file(self,file_path,push_path,name,show=False):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
        res = run_cmd(['adb','-s',device,'push',file_path,push_path+name])
        if not res[0]:
            if show:main_window.show_error_singal.emit('导入失败','',0)
            return 0
        else:
            if show:main_window.show_info_singal.emit('导入成功','')
            return 1
    def pull_file(self,file_path,save_path,name,show=False):
        device = self.get_device()
        if device=='':
            self.show_no_device_error()
        res=run_cmd(['adb','-s',device,'pull',file_path+name,save_path+name],encoding='gbk')
        if not res[0]:
            if show:main_window.show_error_singal.emit('导出失败','',0)
            return 0
        else:
            if show:
                if save_path != '../temp/':main_window.show_info_singal.emit('导出成功','')
            return 1
    def get_file(self,adb_path,mode='default'):
        device=self.get_device()
        adb_path = adb_path.replace("(", "\\(").replace(")", "\\)").replace(" ", r"\ ")
        if self.info['is_root'] != '已开启':
            res1=run_cmd(f'adb -s {device} shell ls -la {adb_path}')
            if 'Permission denied' in res1[1]:
                main_window.show_error_singal.emit('权限不足,请root后重试','',0)
                return 0
            res2=run_cmd(f'adb -s {device} shell ls -a {adb_path}')
        else:
            res1 = run_cmd(f'adb -s {device} shell su -c \'ls -la {adb_path}\'')
            res2 = run_cmd(f'adb -s {device} shell su -c \'ls -a {adb_path}\'')
        if not res2[0]:
            main_window.show_error_singal.emit('该目录不存在或获取失败','',0)
            return 0
        data={}
        temp={}
        info=res1[1].split('\n')[3:]
        name=res2[1].split('\n')[2:]
        for i in range(len(info)):
            if info[i][0] in ['d']:
                data[name[i]]='doc'
            elif info[i][0] in ['l']:
                data[name[i]]='link'
            else:
                if mode=='default':temp[name[i]]='file'
                else:data[name[i]]='file'
        for i in temp.keys():
            data[i]=temp[i]
        return data
    def set_input(self,name):
        def start():
            device=self.get_device()
            if device=='':
                self.show_no_device_error()
                return 0
            mid=self.info['keyboard'][name]
            res = run(args=["adb", "-s", device, "shell", "ime", "enable", mid], cwd="./adb/",
                      stdout=PIPE,
                      stderr=PIPE, shell=True)
            obj = compile(r"b'Input method (?P<newmid>.*?): ")
            newmid = obj.findall(str(res.stdout))[0]
            res = run(args=["adb", "-s", device, "shell", "ime", "set", newmid], cwd="./adb/",
                      stdout=PIPE,
                      stderr=PIPE, shell=True)
            main_window.show_info_singal.emit('设置成功','')
        Thread(target=start).start()
    def get_input(self):
        device= self.get_device()
        if device == '':
            self.show_no_device_error()
            return 0
        res=run_cmd("adb shell ime list -a")
        mid = Re_obj.mid.findall(res[1])
        data = dict()
        for i in range(len(mid)):
            data[mid[i].split('/')[0]] = mid[i]
        self.info['keyboard']=data
        return data
    def kill_all(self):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
            return
        n=0
        for i in self.info['ps'].keys():
            res = run_cmd(f'adb -s {device} shell kill -9 {self.info["ps"][i][0]}')
            n+=1
        main_window.show_info_singal.emit('操作成功', f'尝试停止了{n}个进程')
    def kill_ps(self,num):
        device=self.get_device()
        if device=='':
            self.show_no_device_error()
            return
        res = run_cmd(f'adb -s {device} shell kill -9 {num}')
        if res[0]:
            main_window.show_info_singal.emit('操作成功', res[1])
            return 1
        else:
            main_window.show_error_singal.emit('操作失败', res[1],0)
            return 0
    def get_ps(self,mode='3'):
        device=self.get_device()
        if device=='':
            self.show_no_device_error()
            return
        res = run(f'adb -s {device} shell ps', shell=True, encoding='utf-8', cwd='./adb/', stdout=PIPE)
        info = res.stdout.split('\n')
        data = dict()
        for i in info[1:]:
            try:
                k = i.split()
                name = k[-1]
                pid = k[1]
                sys = k[0]
            except:
                name = ''
                pid = ''
                sys = ''
            if Re_obj.ps_name.findall(name) != []:
                if mode=='all':
                    data[name] = [pid, 'sys' if sys[0] != 'u' else 'user']
                elif mode=='3' and sys[0] == 'u':
                    data[name] = [pid, 'user']
                elif mode=='system' and sys[0] !='u':
                    data[name] = [pid, 'sys']
        self.info['ps']=data
        return data
    def save_app(self,package,path='../temp/',show_info=False,wait=False):
        def start(save_path):
            device=self.get_device()
            if device=='':
                self.show_no_device_error()
                return 0
            res=run_cmd(f'adb -s {device} shell pm path {package}')
            res=run_cmd(f'adb -s {device} pull {res[1].replace("package:","")} {save_path}{package}.apk')
            if show_info:
                if not res[0]:
                    main_window.show_error_singal.emit('操作失败', res[1],0)
                else:
                    main_window.show_info_singal.emit('操作成功', '')
        save_path = path
        if path == 'choose':
            file = QFileDialog.getExistingDirectory(parent=main_window, caption="选取指定文件夹", directory=desktop_path)
            save_path = file+'\\'
        t=Thread(target=lambda :start(save_path=save_path))
        t.start()
        if show_info or wait:t.join()
    def uninstall_app(self,package):
        def start():
            pipe2 = Popen("adb -s " + self.get_device() + " shell", cwd="./adb/", stdin=PIPE, stdout=PIPE, shell=True)
            code2 = pipe2.communicate(
                str.encode("\n" + "pm uninstall " + package + "\n"))
            main_window.show_info_singal.emit('操作成功', '')
        if self.get_device()=='':
            self.show_no_device_error()
            return 0
        Thread(target=start).start()
    def start_app(self,package,activity=None):
        def start(activity):
            device=self.get_device()
            if activity:
                res=run_cmd(f'adb -s {device} shell am start -n {package}/{str(activity).replace(package,"")}')
                if not res[0]:
                    main_window.show_error_singal.emit('操作失败',res[1],0)
                else:
                    main_window.show_info_singal.emit('操作成功', '')
            else:
                self.save_app(package=package,path='../temp/')
                activity=self.get_apk_info(show_func=None,apk_path=f'../temp/{package}.apk')[0]
                if activity=='':
                    main_window.show_error_singal.emit('操作失败', '无法检测应用activity名',0)
                    return
                res=run_cmd(f'adb -s {device} shell am start -n {package}/{str(activity).replace(package,"")}')
                if not res[0]:
                    main_window.show_error_singal.emit('操作失败',res[1],0)
                else:
                    main_window.show_info_singal.emit('操作成功', '')
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
            return 0
        Thread(target=lambda :start(activity)).start()

    def freeze_on(self,package):
        if self.get_device()=='':
            self.show_no_device_error()
            return 0
        res=run_cmd(f'adb -s {self.get_device()} shell pm disable-user {package}')
        if res[0]:return 1
        else:return 0
    def freeze_off(self,package):
        if self.get_device()=='':
            self.show_no_device_error()
            return 0
        res = run_cmd(f'adb -s {self.get_device()} shell pm enable {package}')
        if res[0]:
            return 1
        else:
            return 0
    def push_lock(self):
        if self.get_device()=='':
            self.show_no_device_error()
            return 0
        self.device=self.get_device()
        run_cmd(f'adb -s {self.device} push ./adb/push /sdcard/push')
        res=run_cmd(f'adb -s {self.device} shell ls /sdcard/')
        if 'push' not in res[1]:
            run_cmd(f'adb -s {self.device} shell am start com.xtc.selftest/.ui.ControllerActivity')
            w = InfoBar(
                icon=InfoBarIcon.INFORMATION,
                title='正在解锁',
                content='请打开\'充电时可使用\'和\'打开串口\'选项,然后返回桌面',
                orient=Qt.Horizontal,  # vertical layout
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=main_window
            )
            w.show()
    def delete_file(self,path,stat='file',show_info=False):
        self.device=self.get_device()
        path = path.replace("(", r"\(").replace(")", r"\)").replace(" ",r"\ ")
        res=run_cmd(f'adb -s {self.device} shell rm -{"f" if stat=="file" else "rf"} {path}',encoding='gbk')
        if res[0]:
            if show_info:main_window.show_info_singal.emit('删除成功','')
            return 1
        else:
            if show_info:main_window.show_error_singal.emit('删除失败','',0)
            return 0
    def get_apk_icon(self,apk_path:str,icon_path:str,save_name:str):
        zip=ZipFile(apk_path)
        icon_data=zip.read(icon_path)
        save_path=f'./temp/{save_name}.png'
        with open(save_path, 'w+b') as saveIconFile:
            saveIconFile.write(icon_data)
        return save_path

    def get_apk_info(self,show_func,apk_path:str,apk_name=None,show_data_func=None):
        if apk_name==None:
            apk_basename=path.basename(apk_path)
            apk_basename=apk_basename.split('.')[0]
        else:apk_basename=apk_name
        # res=run_cmd(code=['aapt', 'd', 'badging', apk_path])
        res = run(args=['aapt', 'd', 'badging',apk_path],
                  cwd="./adb/",
                  stdout=PIPE,
                  stderr=PIPE, shell=True,encoding='utf-8')
        info=str(res.stdout)
        if show_data_func:
            show_data_func(info)
        try:
            package=Re_obj.package.findall(info)[0]
        except:
            package = ''
        try:
            real_name=Re_obj.real_name.findall(info)[0]
        except:
            real_name=''
        try:
            activity_name=Re_obj.activity_name.findall(info)[0]
        except:
            activity_name=''
        try:
            sdk_ver=Re_obj.sdk_ver.findall(info)[0]
            name=self.sdk.get(sdk_ver,'未知')
            sdk_ver=sdk_ver+f'({name})'
        except:
            sdk_ver=''
        try:
            highest_ver=Re_obj.highest_ver.findall(info)[0]
            name = self.sdk.get(highest_ver, '未知')
            highest_ver = highest_ver + f'({name})'
        except:
            highest_ver=''
        try:
            icon_path=Re_obj.icon_path.findall(info)
            icon_path=icon_path[0]
        except:
            icon_path=''
        try:
            if apk_path.startswith('..'):apk_path=apk_path[1:]
            size=str(stat(apk_path).st_size//1024**2)
        except:
            size=''
        try:
            if apk_path.startswith('..'):apk_path=apk_path[1:]
            save_icon_path=self.get_apk_icon(icon_path=icon_path,apk_path=apk_path,save_name=apk_basename)
        except:
            save_icon_path=''
        if show_func:
            show_func(package=package,activity=activity_name,sdk_ver=sdk_ver,highest_ver=highest_ver,icon=save_icon_path,size=size+'kb',real_name=real_name)
        else:
            return activity_name,sdk_ver,highest_ver,save_icon_path,size,real_name
    def apk_install(self,func,apk_list:list):
        def reload_result(res: tuple,apk_name):
            try:
                if not res[0]:
                    main_window.show_error_singal.emit('安装错误',res[1],0)
                    data_inserter(main_window.app_installer.ui.data_text, data=(0,f'{self.apk_name}安装失败\n'))
                    QApplication.processEvents()
                    return 0
                return 1
            except Exception as e:
                print(e,e.__traceback__.tb_lineno)
                return 0
        def start_thread():
            main_window.app_installer.ui.install_btn.setEnabled(False)
            main_window.app_installer.ui.push_lock_btn.setEnabled(False)
            widget = main_window.app_installer.ui.data_text
            for i in apk_list:
                self.push_name = path.basename(i)
                self.apk_name = self.push_name.replace("(", "\\(").replace(")", "\\)").replace(" ",r"\ ")
                stat_tool.setContent(f'正在安装{self.push_name}')
                widget.append(f'{self.push_name}开始安装')
                if func == '通用模式':
                    device = self.get_device()
                    try:
                        res_push = run_cmd(['adb', '-s', device, 'push', i, f'/sdcard/{self.push_name}'])
                        data_inserter(widget,data=res_push)
                        QApplication.processEvents()
                        if not reload_result(res_push,self.push_name):continue
                        pipe = Popen("adb -s " + device + " shell", cwd="./adb/", stdin=PIPE, stdout=PIPE,stderr=PIPE, shell=True,encoding='utf-8')
                        res_num = pipe.communicate("\n" + "pm install-create" + "\n")
                        num = Re_obj.install.findall(str(res_num[0]))
                        if num == []:
                            data_inserter(widget,
                                          data=(0, res_num[1]))
                            reload_result((0,res_num),self.apk_name)
                            continue
                        else:data_inserter(widget,data=(1, res_num[0]))
                        QApplication.processEvents()
                        pipe = Popen("adb -s " + device + " shell", cwd="./adb/", stdin=PIPE, stdout=PIPE, shell=True,stderr=PIPE,
                                     encoding='utf-8')
                        res_ready=pipe.communicate(f"pm install-write {num[0]} force /sdcard/{self.apk_name}")
                        QApplication.processEvents()
                        print(res_ready,res_ready[0]!='')
                        if res_ready[0]!='':
                            data_inserter(widget,data=(1, res_ready[0]))
                        else:
                            data_inserter(widget,data=(0, res_num[1]))
                            reload_result((0,res_ready[1]),self.push_name)
                            continue
                        QApplication.processEvents()
                        pipe = Popen("adb -s " + device + " shell", cwd="./adb/", stdin=PIPE, stdout=PIPE,stderr=PIPE, shell=True,
                                     encoding='utf-8')
                        res_install=pipe.communicate(f'pm install-commit {num[0]}')
                        print(res_install)
                        if res_install[0] != '':
                            data_inserter(widget,
                                          data=(1, res_install[0]))
                        else:
                            data_inserter(widget,
                                          data=(0,res_install[1]))
                            reload_result((0, res_install[1]),self.push_name)
                            continue
                        QApplication.processEvents()
                        data_inserter(widget, data=(1,f'{self.push_name}安装成功\n'))
                    except Exception as e:
                        reload_result((0,str(e)),self.push_name)
                elif func=='ROOT模式':
                    device=self.get_device()
                    try:
                        self.apk_name=path.basename(i)
                        print(f'adb -s {device} install -r {i}')
                        res=run_cmd(f'adb -s {device} install -r "{i}"')
                        data_inserter(widget,
                                      data=res)
                        if not reload_result(res,self.apk_name):continue
                        data_inserter(widget, data=(1,f'{self.push_name}安装成功\n'))
                    except Exception as e:
                        reload_result((0,str(e)),self.apk_name)

                elif func=='PM模式':
                    try:
                        device=self.get_device()
                        self.apk_name = path.basename(i)
                        res_push = run_cmd(['adb', '-s', device, 'push', i, f'/sdcard/{self.push_name}'])
                        data_inserter(widget,
                                      data=res_push)
                        print(res_push)
                        # if reload_result(res_push,self.push_name):continue
                        print(f'adb -s {device} shell pm install -r /sdcard/{self.apk_name}')
                        res_install = run_cmd(f'adb -s {device} shell pm install -r /sdcard/{self.apk_name}')
                        print(res_install)
                        data_inserter(widget,
                                      data=res_install)
                        if not reload_result(res_install,self.apk_name):continue
                        data_inserter(widget, data=(1,f'{self.push_name}安装成功\n'))

                    except Exception as e:
                        reload_result((0,str(e)))
                self.delete_file(path=f'/sdcard/{self.push_name}')
            stat_tool.setState(True)
            stat_tool.setContent('安装任务完成!')
            stat_tool.setTitle('完成!')
            stat_tool.closeButton.clicked.emit()
            stat_tool.deleteLater()
            main_window.app_installer.ui.install_btn.setEnabled(True)
            main_window.app_installer.ui.push_lock_btn.setEnabled(True)
        if self.get_device()=='':
            self.show_no_device_error()
            return
        if apk_list!=[]:
            stat_tool = New_StateToolTip(title='安装中...', content='正在安装', parent=main_window)
            stat_tool.show()
            t=Thread_result(func=start_thread)
            t.start()
            stat_tool.closeButton.clicked.connect(lambda :(main_window.app_installer.ui.install_btn.setEnabled(True),main_window.app_installer.ui.push_lock_btn.setEnabled(True),t.stop()))
    def get_devices(self):  # 获取设备连接device名称
        devices = run_cmd("adb devices")
        devices = Re_obj.device.findall(devices[1])
        choice = self.get_device()
        main_window.title_bar.combobox.clear()
        main_window.title_bar.combobox.addItems(devices)
        if choice in devices:
            main_window.title_bar.combobox.setCurrentText(choice)
            main_window.home.ui.label.setText('设备:'+choice)
        elif devices != []:
            main_window.home.ui.init_info()
            main_window.home.ui.label.setText('设备:' + devices[0])
        else:
            main_window.home.ui.label.setText('设备:--')
        if devices == []:
            return 0
        else:
            return 1

    def setting_size(self,size=None):
        device = self.get_device()
        if size == None:
            size = ""
        SIZE = run_cmd("adb -s {} shell wm size {}".format(device, str(size)))
        if size != '':
            main_window.show_info_singal.emit('修改成功!', '')
        if SIZE[0]:
            res = str(SIZE[1]).split("\n")
            if len(res) == 1:
                self.info["size"]=[res[0].split()[-1],res[0].split()[-1]]
                return 1, res[0].split()[-1], res[0].split()[-1]
            else:
                self.info["size"]=[res[1].split()[-1], res[0].split()[-1]]
                return 1, res[1].split()[-1], res[0].split()[-1]
        else:
            self.info["size"]=["--","--"]
            return 0, "--"

    def setting_density(self,dpi=None):
        device = self.get_device()
        if dpi == None:
            dpi = ""
        DPI = run_cmd("adb -s {} shell wm density {}".format(device, str(dpi)))
        if dpi != '':
            main_window.show_info_singal.emit('修改成功!', '')
        if DPI[0]:
            res = str(DPI[1]).split("\n")
            if res == ['']:
                return 0, "--"
            elif len(res) == 1:
                self.info["dpi"]=[res[0].split()[-1], res[0].split()[-1]]
                return 1, res[0].split()[-1], res[0].split()[-1]
            else:
                self.info["dpi"]=[res[1].split()[-1], res[0].split()[-1]]
                return 1, res[1].split()[-1], res[0].split()[-1]
        else:
            return 0, "--"

    def get_doc_used(self):
        device = self.get_device()
        sdcard_df = run_cmd("adb -s {} shell df /sdcard/".format(device))
        root_df = run_cmd("adb -s {} shell df /".format(device))
        sdcard = [i for i in str(sdcard_df[1]).split("\n")[1].split(" ") if i != '']
        sdcard_all = int(sdcard[1]) / 1024 ** 2
        sdcard_used = int(sdcard[2]) / 1024 ** 2
        root = [i for i in str(root_df[1]).split("\n")[1].split(" ") if i != '']
        root_all = int(root[1]) / 1024 ** 2
        root_used = int(root[2]) / 1024 ** 2
        if sdcard_df[0] and root_df[0]:
            self.info["sdcard"]=[sdcard_used,sdcard_all]
            self.info["root"]=[root_used,root_all]
            return 1, [str(sdcard[4]).split('%')[0], sdcard_used, sdcard_all], [str(root[4]).split('%')[0], root_used, root_all]
        else:
            self.info["sdcard"] = ["--", "--"]
            self.info["root"] = ["--", "--"]
            return 0, ["--"], ["__"]

    def get_battery(self):
        device = self.get_device()
        battery = run_cmd("adb -s {} shell dumpsys battery".format(device))
        if battery[0]:
            self.info["battery"]=Re_obj.battery.findall(battery[1])[0]
            return 1, Re_obj.battery.findall(battery[1])[0]
        else:
            self.info["battery"] = "--"
            return 0, "--"

    def get_model(self):
        device = self.get_device()
        model = run_cmd("adb -s {} shell getprop ro.product.model".format(device))
        if model[0]:
            self.info["model"]=model[1]
            return 1, model[1]
        else:
            self.info["model"]="--"
            return 0, "--"

    def get_root(self):
        device = self.get_device()
        if device == '':
            return 0,'--'
        root = run_cmd("adb -s {} shell su -c id".format(device))
        if root[0] == 0:
            self.info["is_root"] = "未开启"
            return 0, "未开启"
        elif "uid=0" in root[1]:
            self.info["is_root"] = "已开启"
            return 1, "已开启"

    def get_android_version(self):
        device = self.get_device()
        ver = run_cmd("adb -s {} shell getprop ro.build.version.release".format(device))
        if ver[0]:
            self.info["version"]=ver[1]
            return 1, ver[1]
        else:
            self.info["version"]="--"
            return 0, "--"

    def get_android_id(self):
        device = self.get_device()
        id = run_cmd("adb -s {} shell settings get secure android_id".format(device))
        if id[0]:
            return 1, id[1]
        else:
            return 0, "--"

    def get_name(self):
        device = self.get_device()
        name = run_cmd("adb -s {} shell getprop ro.product.name".format(device))
        if name[0]:
            self.info["name"]=name[1]
            return 1, name[1]
        else:
            self.info["name"]="--"
            return 0, "--"

    def get_mac(self):
        device = self.get_device()
        mac = run_cmd("adb -s {} shell cat /sys/class/net/wlan0/address".format(device))
        if mac[0]:
            return 1, mac[1]
        else:
            return 0, "--"

    def get_brand(self):
        device = self.get_device()
        brand = run_cmd("adb -s {} shell getprop ro.product.brand".format(device))
        if brand[0]:
            self.info["brand"]=brand[1]
            return 1, brand[1]
        else:
            self.info[brand]="--"
            return 0, "--"

    def get_app(self,mode='all'):
        device = self.get_device()
        if device=='':
            self.show_no_device_error()
            return 0,[]
        if mode=='all':
            mode=''
        elif mode=='system':
            mode='-s'
        elif mode=='3':
            mode='-3'
        app = run_cmd("adb -s {} shell pm list package {}".format(device,mode))
        app_list = []
        for i in str(app[1]).split('\n'):
            app_list.append(i.replace('package:',''))
        if app[0]:
            return 1, app_list
        else:
            return 0, None
class Re_obj():
    device=compile(r"(?P<id>.*?)\tdevice")
    app=compile(r"package:(?P<name>.*?)")
    doc_used=compile("(?P<used>[0-9]+)%")
    battery=compile(r"USB powered: (?P<usb>\w+).*?level: (?P<level>\d+).*?voltage: (?P<voltage>\d+).*?temperature: (?P<temperature>\d+)",S)
    check_update=compile(r'<div class="d" id="info">.*?<div id="filename">小天才专用工具箱</div>.*?<div id="infos">.*?<div id="ready" style="background:#ccc; ">.*?<div id="name".*?<a href="https://lanqinyun.com/.*?>Setup_(?P<ver>.*?).exe</a> </div>',S)
    install = compile(r"Success: created install session \[(?P<num>.*?)]")
    package = compile(r"package: name='(?P<package>.*?)'")
    real_name = compile(r"application: label='(?P<name>.*?)'")
    activity_name = compile(r"launchable-activity: name='(?P<activity>.*?)'")
    sdk_ver = compile(r"sdkVersion:'(?P<minsdk>.*?)'")
    highest_ver = compile(r"targetSdkVersion:'(?P<targetsdk>.*?)'")
    icon_path = compile(r"application: label='.*?' icon='(?P<icon>.*?)'")
    app_path = compile(r"package:(?P<id>.*?)")
    ps_name = compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
    mid = compile(r".*?mId=(?P<mid>.*?) mSettingsActivityName=",S)
    input_name = compile(r"packageName=(?P<name>.*?)\n",S)
class Thread_result(Thread):
    def __init__(self, func,mutex=True,args=(),finish=lambda :()):
        super(Thread_result, self).__init__()
        self.func = func
        self.args = args
        self.mutex=mutex
        self.finish = finish
    def run(self):
        if self.mutex:
            lock=RLock()
            lock.acquire()
            self.result = self.func(*self.args)
            self.finish()
            lock.release()
        else:self.result = self.func(*self.args)
    def get_result(self):
        Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None
    def stop(self):
        Event().set()
class Qt_Thread(QThread):
    def __init__(self,func):
        super(Qt_Thread,self).__init__()
        self.func=func
    def run(self):
        self.func()
def run_cmd(code,cwd="./adb/",check=True,encoding="utf-8",thread=(True,True)): # thread=(是否使用多线程，是否开启进程锁)
    def start(code,cwd,encoding):
        res=run(args=code,cwd=cwd,stdout=PIPE,stderr=PIPE,encoding=encoding,shell=True)
        return 1 if res.stderr == '' else 0,res.stdout.strip("\t\n") if res.stderr == '' else res.stderr.strip("\t\n")
    if thread[0]:
        t=Thread_result(func=start,mutex=thread[1],args=(code,cwd,encoding))
        t.start()
        t.join()
        return t.get_result()
    else:
        return start(code=code,cwd=cwd,encoding=encoding)
def choose_file():
    files,filetype=QFileDialog.getOpenFileNames(main_window,'选择APK文件',desktop_path,"APK Files(*.apk)")
    for i in files:
        main_window.app_installer.ui.tableWidget.add_apk_row(i)
def get_xtc_info(): # 获取当前设备信息
    k=5
    while True:
        try:
            last=xtc.get_device()
            if xtc.get_devices():
                model=xtc.get_model()[1]
                version=xtc.get_android_version()[1]
                root=xtc.get_root()[1]
                id=xtc.get_android_id()[1]
                name=xtc.get_name()[1]
                mac=xtc.get_mac()[1]
                brand=xtc.get_brand()[1]
                if xtc.get_device()!=last and xtc.get_device()!="" and brand!="XTC":
                    main_window.show_error_singal.emit("检测到不是小天才设备","检测到当前设备为"+brand+",并不是小天才手表,这样可能导致部分功能无法使用请悉知",3)
                apk_list = xtc.get_app()[1]
                app_num=len(apk_list)
                if last!=xtc.get_device():
                    k=5
                    main_window.app_manager.ui.set_search(apk_list)
                    main_window.app_manager.ui.ListWidget.clear()
                    main_window.app_manager.ui.ListWidget.addItems(labels=apk_list)
                    ps = xtc.get_ps()
                    main_window.pross_manager.ui.set_search(ps.keys())
                    main_window.pross_manager.ui.ListWidget.clear()
                    main_window.pross_manager.ui.ListWidget.addItems(ps.keys())
                    input_list=xtc.get_input()
                    main_window.keyboard_manager.ui.set_search(input_list.keys())
                    main_window.keyboard_manager.ui.ListWidget.clear()
                    main_window.keyboard_manager.ui.ListWidget.addItems(input_list.keys())
                    file_data=xtc.get_file('/sdcard/')
                    main_window.file_manager.ui.file_list.signal.emit(file_data)
                    main_window.setPath_signal.emit(('','/sdcard/'))
                if k==5:
                    k=0
                    used=xtc.get_doc_used()
                    battery=xtc.get_battery()
                    dpi=xtc.setting_density()
                    size=xtc.setting_size()
                    timeout = int(xtc.screenOffTimeOut()) // 1000
                    speed=xtc.animationScale([])
                    main_window.home.ui.ProgressBar_2.setValue(int(used[1][0]))
                    main_window.home.ui.label_16.setText(used[1][0]+"%")
                    main_window.home.ui.label_15.setText("内部储存: %.2fGB/%.2fGB" % (used[1][1],used[1][2]))
                    main_window.home.ui.ProgressBar_3.setValue(int(used[2][0]))
                    main_window.home.ui.label_18.setText(used[2][0] + "%")
                    main_window.home.ui.label_17.setText("根目录: %.2fGB/%.2fGB" % (used[2][1], used[2][2]))
                    main_window.home.ui.ProgressBar.setValue(int(battery[1][1]))
                    main_window.home.ui.label_19.setText("{}%".format(battery[1][1]))
                    main_window.home.ui.label_10.setText("当前电量: {}".format(battery[1][1]))
                    main_window.home.ui.label_13.setText("温度: %.1f℃" % (int(battery[1][3])//10))
                    main_window.home.ui.label_11.setText("USB: {}".format("已开启" if battery[1][0] in ["true"] else "未开启"))
                    main_window.home.ui.label_12.setText("电压: {}mv".format(battery[1][2]))
                    main_window.home.ui.label_22.setText("当前DPI: {}".format(dpi[1]))
                    main_window.home.ui.label_21.setText("默认DPI: {}".format(dpi[2]))
                    main_window.screen_setting.ui.defaultDPI.setText(f"默认DPI: {dpi[2]}")
                    main_window.screen_setting.ui.currentDPI.setText(f"当前DPI: {dpi[1]}")
                    main_window.home.ui.label_14.setText("当前屏幕大小: {}".format(size[1]))
                    main_window.home.ui.label_20.setText("默认屏幕大小: {}".format(size[2]))
                    main_window.screen_setting.ui.BodyLabel.setText(f'默认分辨率: {size[2]}')
                    main_window.screen_setting.ui.currentSize.setText(f'当前分辨率: {size[1]}')
                    main_window.screen_setting.ui.BodyLabel_2.setText(f'当前屏幕超时时间: {timeout}秒')
                    main_window.screen_setting.ui.animation1Speed.setText(f'窗口动画速度: {speed[0]}x')
                    main_window.screen_setting.ui.animation2Speed.setText(f'过渡动画速度: {speed[1]}x')
                    main_window.screen_setting.ui.animation3Speed.setText(f'动画程序速度: {speed[2]}x')
                    if used[0]==0:
                        main_window.home.ui.ProgressBar_2.setValue(0)
                        main_window.home.ui.ProgressBar_3.setValue(0)
                    if battery[0]==0:
                        main_window.home.ui.ProgressBar.setValue(0)
                        main_window.home.ui.label_13.setText("USB: --")

                k+=1
                main_window.home.ui.label_3.setText("设备型号: {}".format(model)) # 设备名称
                main_window.home.ui.label_6.setText("安卓版本: {}".format(version)) # 安卓版本
                main_window.home.ui.label_7.setText("root权限: {}".format(root)) # root权限
                main_window.home.ui.label_9.setText("安卓ID: {}".format(id)) # 安卓ID
                main_window.home.ui.label_2.setText("设备名称: {}".format(name)) # 设备代号
                main_window.home.ui.label_5.setText("mac地址: {}".format(mac)) # mac地址
                main_window.home.ui.label_4.setText("设备厂商: {}".format(brand)) # 设备厂商
                main_window.home.ui.label_8.setText("应用数量: {}".format(str(app_num))) # 应用数量
            else:
                if last=="":
                    main_window.home.ui.init_info()
        except Exception as e:
            # print(e,e.__traceback__.tb_lineno)
            continue
def start_worker():
    device_thread = Thread(target=get_xtc_info)
    device_thread.daemon = True
    device_thread.start()

def init_window():
    def get_apk_list():
        row_count = main_window.app_installer.ui.tableWidget.rowCount()
        apk_list=[]
        for row in range(row_count):
            item = main_window.app_installer.ui.tableWidget.item(row, 1).text()
            if item != '':
                apk_list.append(item)
        return apk_list
    def del_rows():
        model = main_window.app_installer.ui.tableWidget.selectionModel()
        selected_rows = model.selectedRows()
        for row in reversed(selected_rows):
            index = row.row()
            main_window.app_installer.ui.tableWidget.removeRow(index)
        main_window.app_installer.ui.tableWidget.clearSelection()
    def search_singal(widget_list,widgetres,self):
        def start():
            search_text = self.text()
            res=[]
            for text in widgetres:
                if search_text in text:
                    res.append(text)
            widget_list.clear()
            widget_list.addItems(res)
        Thread(target=start).start()
    def app_list_clicked_event(app_name):
        main_window.app_manager.ui.app_frame.on_load()
        xtc.save_app(app_name,wait=True)
        xtc.get_apk_info(show_func=main_window.app_manager.ui.app_frame.set_info,apk_path=f'../temp/{app_name}.apk',apk_name=app_name,show_data_func=lambda data:(data_inserter(main_window.app_manager.ui.TextEdit.insertPlainText,data=(1,data))))
    def ps_list_clicked_event(ps_name):
        main_window.pross_manager.ui.app_frame.on_load()
        xtc.save_app(ps_name,wait=True)
        xtc.get_apk_info(show_func=main_window.pross_manager.ui.app_frame.set_info,apk_path=f'../temp/{ps_name}.apk',apk_name=ps_name,show_data_func=lambda data:(data_inserter(main_window.pross_manager.ui.TextEdit.insertPlainText,data=(1,data))))
    def input_list_clicked_event(input_name):
        main_window.keyboard_manager.ui.app_frame.on_load()
        xtc.save_app(input_name,wait=True)
        xtc.get_apk_info(show_func=main_window.keyboard_manager.ui.app_frame.set_info,apk_path=f'../temp/{input_name}.apk',apk_name=input_name,show_data_func=lambda data:(data_inserter(main_window.keyboard_manager.ui.TextEdit.insertPlainText,data=(1,data))))
    def file_list_update(name,type):
        try:
            if type in ['link','doc']:
                main_window.file_manager.ui.setPath(('+',name))
                file_path='/'+'/'.join(main_window.file_manager.ui.path)+'/'
                ls_get(file_path)
            else:
                if main_window.file_manager.ui.CheckBox.isChecked():
                    t=Thread_result(func=lambda :(xtc.pull_file(file_path=main_window.file_manager.ui.getPath(),save_path='../temp/',name=name)),finish=lambda :(run_cmd(code=f'start ./temp/{name}',cwd='./')))
                    t.start()
        except:
            pass
    def ls_get(file_path):
        data = xtc.get_file(adb_path=file_path)
        main_window.file_manager.ui.file_list.setCards(data)
        if file_path=='/':main_window.file_manager.ui.back_btn.setEnabled(False)
        else:main_window.file_manager.ui.back_btn.setEnabled(True)
    def flush_file():
        ls_get(main_window.file_manager.ui.getPath())
    def init_link_button():
        sender = main_window.sender()
        ls_get(file_path=main_window.file_manager.ui.link[sender.text()])
        main_window.file_manager.ui.setPath(('',main_window.file_manager.ui.link[sender.text()]))
    def pull_button():
        if main_window.file_manager.ui.file_list.choice == []:
            main_window.show_error_singal.emit('请先选择文件','',0)
            return
        file = QFileDialog.getExistingDirectory(parent=main_window, caption="选取保存文件夹", directory=desktop_path)
        if file == '':
            return
        save_path = file
        save_path = path.normpath(save_path) + '\\'
        show = False
        n = 1
        for i in main_window.file_manager.ui.file_list.choice:
            if n == len(file):
                show = True
            n+=1
            Thread(target=lambda :(xtc.pull_file(file_path=main_window.file_manager.ui.getPath(),save_path=save_path,name=i.name,show = show)),daemon=True).start()
    def push_button():
        file,ok = QFileDialog.getOpenFileNames(main_window,"选取导入文件", desktop_path,'All Files (*)')
        if file == []:
            return
        push_path = main_window.file_manager.ui.getPath()
        show = False
        n = 1
        for i in file:
            if n == len(file):
                show = True
            n+=1
            Thread(target=lambda :(xtc.push_file(file_path=i,push_path=push_path,name=path.basename(i),show = show),main_window.file_manager.ui.flush_btn.clicked.emit()),daemon=True).start()
    def delete_button():
        if main_window.file_manager.ui.file_list.choice == []:
            main_window.show_error_singal.emit('请先选择文件','',0)
            return
        for i in main_window.file_manager.ui.file_list.choice:
            Thread_result(func=lambda :(xtc.delete_file(path=main_window.file_manager.ui.getPath()+i.name,stat='file' if i.type == 'file' else 'doc'),main_window.file_manager.ui.flush_btn.clicked.emit())).start()
        main_window.show_info_singal.emit('删除成功', '')
    def rename_button():
        if main_window.file_manager.ui.file_list.choice == []:
            main_window.show_error_singal.emit('请先选择文件','',0)
            return
        w1=InputMessageBox(title='请输入修改的名称',placeholderText='文件名称...',parent=main_window)
        w1.urlLineEdit.setText(main_window.file_manager.ui.file_list.choice[0].name)
        if w1.exec():
            if w1.urlLineEdit.text() in main_window.file_manager.ui.file_list.card:
                if not main_window.showMessage(signalName='',title='温馨提醒',content='已存在同名文件,是否覆盖?',yesbtn='覆盖',nobtn='取消'):
                    return
            if len(main_window.file_manager.ui.file_list.choice)!=1:
                n=1
                for i in main_window.file_manager.ui.file_list.choice:
                    name = w1.urlLineEdit.text()
                    k = path.splitext(name)
                    name = k[0]+f'({n})'+k[-1]
                    xtc.rename_file(file_path=main_window.file_manager.ui.getPath(),old_name=i.name,new_name=name)
                    n+=1
            else:
                xtc.rename_file(file_path=main_window.file_manager.ui.getPath(),old_name=main_window.file_manager.ui.file_list.choice[0].name,new_name=w1.urlLineEdit.text())
            flush_file()
            main_window.show_info_singal.emit('重命名成功', '')
    def new_button():
        w1 = InputMessageBox(title='请输入创建的文件夹名称', placeholderText='文件夹名称...', parent=main_window)
        n=0
        for i in main_window.file_manager.ui.file_list.card:
            if '新建文件夹(' in i:
                n+=1
        w1.urlLineEdit.setText(f'新建文件夹({n})' if n!=0 else '新建文件夹')
        if w1.exec():
            if w1.urlLineEdit.text() in main_window.file_manager.ui.file_list.card:
                if not main_window.showMessage(signalName='',title='温馨提醒', content='已存在同名文件夹,是否覆盖?', yesbtn='覆盖',
                                               nobtn='取消'):
                    return
            xtc.new_doc(path=main_window.file_manager.ui.getPath(),name=w1.urlLineEdit.text())
            flush_file()
    def copy_button():
        path = main_window.file_manager.ui.getPath()
        for i in main_window.file_manager.ui.file_list.choice:
            main_window.file_manager.ui.copy.append(path + i.name)
        main_window.file_manager.ui.cut.clear()
        main_window.show_info_singal.emit('复制成功','')
    def cut_button():
        path = main_window.file_manager.ui.getPath()
        for i in main_window.file_manager.ui.file_list.choice:
            main_window.file_manager.ui.cut.append(path+i.name)
        main_window.file_manager.ui.copy.clear()
        main_window.show_info_singal.emit('剪切成功','')
    def paste_button():
        path=main_window.file_manager.ui.getPath()
        if main_window.file_manager.ui.copy!=[]:
            for i in main_window.file_manager.ui.copy:
                Thread(target=lambda :(xtc.paste_file(old_path=i,new_path=path,mode='copy'),main_window.file_manager.ui.flush_btn.clicked.emit())).start()
            main_window.show_info_singal.emit('粘贴成功', '')
        elif main_window.file_manager.ui.cut != []:
            for i in main_window.file_manager.ui.cut:
                Thread(target=lambda :(xtc.paste_file(old_path=i,new_path=path,mode='cut'),main_window.file_manager.ui.flush_btn.clicked.emit())).start()
            main_window.show_info_singal.emit('粘贴成功', '')
    def get_file_info_event():
        sender=main_window.file_manager.ui.file_list.sender()
        info=xtc.get_file_info(type=sender.type,file_path=main_window.file_manager.ui.getPath() + sender.name)
        main_window.setFileName.emit(sender.name)
        type = ''
        if sender.type == 'doc':
            type = '文件夹'
        elif sender.type == 'link':
            type = '快捷方式'
        elif '.' not in sender.name:
            type = '文件'
        else:
            file_type = str(sender.name).split('.')[-1]
            type = f'{file_type}文件'
        main_window.file_manager.ui.file_info_frame.file_type.setText(f'文件类型:{type}')
        main_window.file_manager.ui.file_info_frame.file_time.setText(f'修改时间:{info[1]}')
        main_window.file_manager.ui.file_info_frame.file_size.setText(f'文件大小:{info[0]}')
        main_window.file_manager.ui.file_info_frame.icon.setIcon(sender.icon)
    def fileSearchFunc():
        def fileSearchListChilckFunc():
            def start():
                text=w.listWidget.currentItem().text()
                name = text.split('/')[-1]
                path = text[0:-len(name)]
                file_data = xtc.get_file(path)
                main_window.file_manager.ui.file_list.signal.emit(file_data)
                main_window.setPath_signal.emit(('', path))
                for i in main_window.file_manager.ui.file_list.widget:
                    if i.name == name:
                        i.setSelected(True)
            Thread(target=start).start()
        w=FileSearchResWidget(parent=main_window.file_manager)
        w.show()
        w.addFileSignal.connect(w.addFileFunc)
        w.listWidget.clicked.connect(fileSearchListChilckFunc)
        xtc.find_file(cwd=main_window.file_manager.ui.getPath(),key=main_window.file_manager.ui.search_file.text(),widget=w)

    def chooseFile(pathWidget):
        file = QFileDialog.getExistingDirectory(parent=main_window, caption="选取指定文件夹",
                                                directory=desktop_path)
        if file:
            save_path = file
            save_path = path.normpath(save_path) + '\\'
            pathWidget.setText(save_path)
        else:
            pass
    def buttonScrcpyEvent():
        if main_window.screen_setting.ui.CheckBox.isChecked():
            Thread(target=lambda :xtc.scrcpy(record=True,savePath=main_window.screen_setting.ui.savePath.text())).start()
        else:
            Thread(target=lambda: xtc.scrcpy(record=False)).start()
    def buttonScreenShotEvent():
        Thread(target=lambda :(xtc.screenShot(savePath=main_window.screen_setting.ui.savePath_2.text()))).start()
    def buttonSetDPIevent():
        if xtc.get_device() == '':
            xtc.show_no_device_error()
            return
        dpi = main_window.screen_setting.ui.setDPIedit.text()
        sender = main_window.screen_setting.ui.setDPI.sender()
        if sender.text() == '恢复默认':
            dpi = xtc.info['dpi'][1]
        if dpi == '':
            main_window.show_error_singal.emit('请输入值','',0)
            return
        Thread(target=lambda :(xtc.setting_density(dpi=dpi))).start()
        main_window.screen_setting.ui.currentDPI.setText(f'当前DPI: {dpi}')
    def buttonSetSizeEvent():
        if xtc.get_device() == '':
            xtc.show_no_device_error()
            return
        w = main_window.screen_setting.ui.setWEdit.text()
        h = main_window.screen_setting.ui.setHEdit.text()
        sender = main_window.screen_setting.ui.setSize.sender()
        if sender.text() == '恢复默认':
            size = xtc.info['size'][1]
            Thread(target=lambda: (xtc.setting_size(size=size))).start()
            main_window.screen_setting.ui.currentSize.setText(f'当前屏幕分辨率: {size}')
            return
        if w == '' or h == '':
            main_window.show_error_singal.emit('请输入值','',0)
            return
        Thread(target=lambda :(xtc.setting_size(size=w+'x'+h))).start()
        main_window.screen_setting.ui.currentSize.setText(f'当前分辨率: {w}x{h}')
    def setTimeOut():
        timeout = int(main_window.screen_setting.ui.setTimeoutEdit.text())*1000
        Thread(target=lambda :(xtc.screenOffTimeOut(timeout = str(timeout)),main_window.show_info_singal.emit('修改成功!',''))).start()
        main_window.screen_setting.ui.BodyLabel_2.setText(f'当前屏幕超时时间: {timeout//1000}秒')
    def buttonWindowSpeed():
        speed = main_window.screen_setting.ui.setAnimation1Speed.text()
        if speed.isalnum() or speed == '':
            main_window.show_error_singal.emit('请输入正确的数值','',0)
            return 0
        Thread(target=lambda :(xtc.animationScale(speed=[speed,None,None]))).start()
        main_window.screen_setting.ui.animation1Speed.setText(f'窗口动画速度: {speed}x')
    def buttonTransitionSpeed():
        speed = main_window.screen_setting.ui.setAnimation2Speed.text()
        if speed.isalnum() or speed == '':
            main_window.show_error_singal.emit('请输入正确的数值','',0)
            return 0
        Thread(target=lambda :(xtc.animationScale(speed=[None,speed,None]))).start()
        main_window.screen_setting.ui.animation1Speed.setText(f'过渡动画速度: {speed}x')
    def buttonAnimatorSpeed():
        speed = main_window.screen_setting.ui.setAnimation3Speed.text()
        if speed.isalnum() or speed == '':
            main_window.show_error_singal.emit('请输入正确的数值','',0)
            return 0
        Thread(target=lambda :(xtc.animationScale(speed=[None,None,speed]))).start()
        main_window.screen_setting.ui.animation1Speed.setText(f'动画程序速度: {speed}x')

    main_window.app_installer.ui.PushButton_3.clicked.connect(choose_file)
    main_window.app_installer.ui.PushButton_4.clicked.connect(del_rows)
    main_window.app_installer.ui.action1.triggered.connect(lambda :xtc.apk_install(func='通用模式',apk_list=get_apk_list()))
    main_window.app_installer.ui.action2.triggered.connect(lambda :xtc.apk_install(func='ROOT模式',apk_list=get_apk_list()))
    main_window.app_installer.ui.action3.triggered.connect(lambda :xtc.apk_install(func='PM模式',apk_list=get_apk_list()))
    main_window.app_installer.ui.tableWidget.set_mouse_press_func(lambda text:xtc.get_apk_info(apk_path=text,show_func=main_window.app_installer.ui.apk_info.set_info))
    main_window.app_installer.ui.push_lock_btn.clicked.connect(xtc.push_lock)
    main_window.app_manager.ui.search_edit.searchSignal.connect(lambda :search_singal(widget_list=main_window.app_manager.ui.ListWidget,widgetres=xtc.get_app()[1],self=main_window.app_manager.ui.search_edit))
    main_window.app_manager.ui.flush_all.clicked.connect(lambda :(main_window.app_manager.ui.ListWidget.clear(),main_window.app_manager.ui.ListWidget.addItems(xtc.get_app(mode='all')[1],show=main_window.app_manager.ui.set_search)))
    main_window.app_manager.ui.flush_system.clicked.connect(lambda :(main_window.app_manager.ui.ListWidget.clear(),main_window.app_manager.ui.ListWidget.addItems(xtc.get_app(mode='system')[1],show=main_window.app_manager.ui.set_search)))
    main_window.app_manager.ui.flush_3.clicked.connect(lambda :(main_window.app_manager.ui.ListWidget.clear(),main_window.app_manager.ui.ListWidget.addItems(xtc.get_app(mode='3')[1],show=main_window.app_manager.ui.set_search)))
    main_window.app_manager.ui.freeze_on.clicked.connect(lambda :(xtc.freeze_on(package=main_window.app_manager.ui.ListWidget.currentItem().text())))
    main_window.app_manager.ui.freeze_off.clicked.connect(lambda :(xtc.freeze_off(package=main_window.app_manager.ui.ListWidget.currentItem().text())))
    main_window.app_manager.ui.start_app.clicked.connect(lambda :(xtc.start_app(package=main_window.app_manager.ui.ListWidget.currentItem().text())))
    main_window.app_manager.ui.get_apk.clicked.connect(lambda :(xtc.save_app(package=main_window.app_manager.ui.ListWidget.currentItem().text(),path='choose',show_info=True)))
    main_window.app_manager.ui.uninstall_app.clicked.connect(lambda :(xtc.uninstall_app(package=main_window.app_manager.ui.ListWidget.currentItem().text())))
    main_window.app_manager.ui.ListWidget.set_clicked_func(func=app_list_clicked_event)
    main_window.pross_manager.ui.ListWidget.set_clicked_func(func=ps_list_clicked_event)
    main_window.pross_manager.ui.search_edit.searchSignal.connect(lambda :search_singal(widget_list=main_window.pross_manager.ui.ListWidget,widgetres=xtc.get_ps(mode='all').keys(),self=main_window.pross_manager.ui.search_edit))
    main_window.pross_manager.ui.flush_3.clicked.connect(lambda :(main_window.pross_manager.ui.ListWidget.clear(),main_window.pross_manager.ui.ListWidget.addItems(xtc.get_ps(mode='3').keys(),show=main_window.pross_manager.ui.set_search)))
    main_window.pross_manager.ui.flush_all.clicked.connect(lambda :(main_window.pross_manager.ui.ListWidget.clear(),main_window.pross_manager.ui.ListWidget.addItems(xtc.get_ps(mode='all').keys(),show=main_window.pross_manager.ui.set_search)))
    main_window.pross_manager.ui.flush_system.clicked.connect(lambda :(main_window.pross_manager.ui.ListWidget.clear(),main_window.pross_manager.ui.ListWidget.addItems(xtc.get_ps(mode='system').keys(),show=main_window.pross_manager.ui.set_search)))
    main_window.pross_manager.ui.kill_ps.clicked.connect(lambda :(xtc.kill_ps(num=xtc.info['ps'][main_window.pross_manager.ui.ListWidget.currentItem().text()][0]),main_window.pross_manager.ui.flush_3.clicked.emit()))
    main_window.pross_manager.ui.kill_all.clicked.connect(lambda :(xtc.kill_all(),main_window.pross_manager.ui.flush_3.clicked.emit()))
    main_window.keyboard_manager.ui.PushButton.clicked.connect(lambda :(xtc.set_input(name=main_window.keyboard_manager.ui.ListWidget.currentItem().text())))
    main_window.keyboard_manager.ui.flush.clicked.connect(lambda :(main_window.keyboard_manager.ui.ListWidget.clear(),main_window.keyboard_manager.ui.ListWidget.addItems(xtc.get_input().keys())))
    main_window.keyboard_manager.ui.search_edit.searchSignal.connect(lambda :search_singal(widget_list=main_window.keyboard_manager.ui.ListWidget,widgetres=xtc.get_input().keys(),self=main_window.keyboard_manager.ui.search_edit))
    main_window.keyboard_manager.ui.ListWidget.set_clicked_func(func=input_list_clicked_event)
    main_window.file_manager.ui.file_list.update_func=file_list_update
    main_window.file_manager.ui.PrimaryPushButton.clicked.connect(lambda :(ls_get(main_window.file_manager.ui.path_widget.text()),main_window.file_manager.ui.setPath(('',main_window.file_manager.ui.path_widget.text()))))
    main_window.file_manager.ui.back_btn.clicked.connect(lambda :ls_get(main_window.file_manager.ui.setPath(('-'))))
    main_window.file_manager.ui.flush_btn.clicked.connect(flush_file)
    main_window.file_manager.ui.init_link_func = init_link_button
    main_window.file_manager.ui.init_file_link()
    main_window.file_manager.ui.pull_btn.clicked.connect(pull_button)
    main_window.file_manager.ui.push_btn.clicked.connect(push_button)
    main_window.file_manager.ui.del_btn.clicked.connect(delete_button)
    main_window.file_manager.ui.set_name_btn.clicked.connect(rename_button)
    main_window.file_manager.ui.new_btn.clicked.connect(new_button)
    main_window.file_manager.ui.copy_btn.clicked.connect(copy_button)
    main_window.file_manager.ui.cut_btn.clicked.connect(cut_button)
    main_window.file_manager.ui.paste_btn.clicked.connect(paste_button)
    main_window.file_manager.ui.file_list.push_func = lambda name,show:Thread(target=lambda :(xtc.push_file(file_path=name,push_path=main_window.file_manager.ui.getPath(),name=path.basename(name),show=show),main_window.file_manager.ui.flush_btn.clicked.emit()),daemon=True).start()
    main_window.file_manager.ui.file_list.chioce_mode_widget = main_window.file_manager.ui.CheckBox_2
    main_window.file_manager.ui.selected_all_btn.clicked.connect(lambda :main_window.file_manager.ui.file_list.selected_func(mode='all'))
    main_window.file_manager.ui.selected_cancel_btn.clicked.connect(lambda :main_window.file_manager.ui.file_list.selected_func(mode='none'))
    main_window.file_manager.ui.selected_file.clicked.connect(lambda :main_window.file_manager.ui.file_list.selected_func(mode='file'))
    main_window.file_manager.ui.selected_doc.clicked.connect(lambda :main_window.file_manager.ui.file_list.selected_func(mode='doc'))
    main_window.file_manager.ui.selected_reverse_btn.clicked.connect(lambda :main_window.file_manager.ui.file_list.selected_func(mode='reverse'))
    main_window.file_manager.ui.file_list.chick_card_func = lambda :Thread(target=get_file_info_event).start()
    main_window.file_manager.ui.search_file.searchSignal.connect(fileSearchFunc)
    main_window.screen_setting.ui.savePath.setText(desktop_path+'\\')
    main_window.screen_setting.ui.savePath_2.setText(desktop_path+'\\')
    main_window.screen_setting.ui.startScrcpy.clicked.connect(buttonScrcpyEvent)
    main_window.screen_setting.ui.chooseFile.clicked.connect(lambda :chooseFile(main_window.screen_setting.ui.savePath))
    main_window.screen_setting.ui.chooseFile_2.clicked.connect(lambda :chooseFile(main_window.screen_setting.ui.savePath_2))
    main_window.screen_setting.ui.setDPIbutton.clicked.connect(buttonSetDPIevent)
    main_window.screen_setting.ui.setSizeButton.clicked.connect(buttonSetSizeEvent)
    main_window.screen_setting.ui.setDPIdefault.clicked.connect(buttonSetDPIevent)
    main_window.screen_setting.ui.setSizeDefault.clicked.connect(buttonSetSizeEvent)
    main_window.screen_setting.ui.startscreenshot.clicked.connect(buttonScreenShotEvent)
    main_window.screen_setting.ui.setTimeoutButton.clicked.connect(setTimeOut)
    main_window.screen_setting.ui.setBlackMode.clicked.connect(lambda :Thread(target=lambda :xtc.setTheme(2)).start())
    main_window.screen_setting.ui.setWhiteMode.clicked.connect(lambda :Thread(target=lambda :xtc.setTheme(1)).start())
    main_window.screen_setting.ui.openRotation.clicked.connect(lambda :Thread(target=lambda :xtc.setScreenRotation(1)).start())
    main_window.screen_setting.ui.closeRotation.clicked.connect(lambda :Thread(target=lambda :xtc.setScreenRotation(0)).start())
    main_window.screen_setting.ui.setAnimation1Button.clicked.connect(buttonWindowSpeed)
    main_window.screen_setting.ui.setAnimation2Button.clicked.connect(buttonTransitionSpeed)
    main_window.screen_setting.ui.setAnimation3Button.clicked.connect(buttonAnimatorSpeed)
    main_window.auto_root.ui.PushButton.clicked.connect(lambda :Thread(target=lambda :xtc.autoRoot(mode=main_window.auto_root.ui.Z6_DFBcard.on,insertFunc=main_window.auto_root.ui.TextEdit)).start())
    main_window.auto_root.ui.PushButton_2.clicked.connect(lambda :Thread(target=lambda :xtc.rootBack(insertFunc=main_window.auto_root.ui.TextEdit)).start())
def time_out():
    global xtc
    welcome_window.close()
    main_window.setWindowOpacity(1)
    xtc = XTC_func()
    start_worker()
    init_window()
    w = InfoBar(
        icon=InfoBarIcon.INFORMATION,
        title=user,
        content="欢迎回来，搞表愉快!",
        orient=Qt.Horizontal,  # vertical layout
        isClosable=False,
        position=InfoBarPosition.TOP,
        duration=2000,
        parent=main_window
    )
    w.show()
    if cfg.checkUpdateAtStartUp.value:
        Thread(target=check_update).start()


def not_xtc(brand):
    model=brand
    m=MessageBox(title="检测到不是小天才设备",parent=main_window,content="检测到当前设备为{},并不是小天才,可能导致部分功能无法使用,请悉知。".format(model[1]))
    m.yesButton.setText("我已知晓")
    m.exec()
def check_update():
    try:
        res = get('https://github.com/MXG114514/XTC_box/blob/main/README.md')
        json = findall(r'  <script type="application/json" data-target="react-app.embeddedData">(?P<text>.*?)</script>',
                       res.text)
        info = eval(json[0].replace('false', 'False').replace('true', 'True').replace('null', 'None'))
        md = info['payload']['blob']['richText']
        res = findall(
            r'<h. tabindex="-." class="heading-element" dir="auto">V(?P<ver>.*?):</h.>.*?</path></svg></a></div>\n<p dir="auto">(?P<info>.*?)</p>',
            md)
        k = 0
        info = ''
        for i in res:
            v = i[0]
            if float(v) > k:
                k = float(v)
                info = i[1]
        if k>float(VERSION):
            # m = MessageBox(title="有新版本!",
            #                content="检测到新版本:小天才专用工具箱V{},快去更新体验最新功能吧!(密码:58mr)\n更新日志: {}".format(str(k),info),
            #                parent=main_window)
            # m.yesButton.setText("立即更新")
            # m.cancelButton.setText("暂不更新")
            # if m.exec():
            #     QDesktopServices.openUrl(QUrl("https://wwu.lanzouq.com/b04ewllad"))
            main_window.message.emit('app_ver_check', '有新版本!',
                                     "检测到新版本:小天才专用工具箱V{},快去更新体验最新功能吧!\n更新日志: {}".format(str(k),info),
                                     '立即更新', '暂不更新')
            while 1:
                sleep(0.3)
                try:
                    if main_window.signalInfo['app_ver_check'] != None:
                        if not main_window.signalInfo['app_ver_check']:
                            return 0
                        else:
                            QDesktopServices.openUrl(QUrl("https://pan.baidu.com/s/1Z6eBJdzYJTiFgSF-7XH76A?pwd=ABCD"))
                            break
                except:
                    continue
    except:
        pass

def data_inserter(insert_widget,data:tuple):
    time=datetime.now().strftime("%H-%M-%S")
    state='INFO' if data[0] else 'ERROR'
    insert_widget.append(f'[{time}]({state}):{str(data[1]).strip()}')
    insert_widget.moveCursor(insert_widget.textCursor().End)

if __name__ == '__main__':
    if cfg.get(cfg.dpiScale) in ["Auto",1]:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
    user=environ['USERNAME']
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(argv)
    translator = FluentTranslator()
    app.installTranslator(translator)
    welcome_window=QWidget()
    welcome_window_ui=Welcome_Window()
    welcome_window_ui.setupUi(welcome_window)
    welcome_window.show()
    main_window=Main_Window()
    main_window.setWindowOpacity(0)
    main_window.show()
    main_window.setMinimumWidth(610)
    main_window.titleBar.setMaximumHeight(40)
    timer = QTimer()
    timer.setSingleShot(True)
    timer.setInterval(1200)
    timer.timeout.connect(time_out)
    timer.start()
    exit(app.exec_())