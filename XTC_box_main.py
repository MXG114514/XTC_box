from sys import argv,exit
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QDesktopServices
from config import cfg,VERSION
from XTC_box_ui import Welcome_Window # 开屏动画
from main_window import Main_Window # 主界面
from subprocess import run,PIPE,SubprocessError,Popen
from re import compile,S
from threading import Thread,RLock
from qfluentwidgets import InfoBar,InfoBarPosition,InfoBarIcon,MessageBox,FluentTranslator,StateToolTip
from os import environ,path,stat
from requests import get
from datetime import datetime
from zipfile import ZipFile

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
        self.info={"size":["--","--"],"dpi":["--","--"],"sdcard":["--","--"],"root":["--","--"],"battery":"--","version":"--","name":"--","model":"--","is_root":"--","brand":"--",'ps':{}}
    def show_no_device_error(self):
        w = InfoBar(
            icon=InfoBarIcon.ERROR,
            title='操作错误',
            content='未连接设备!',
            orient=Qt.Horizontal,  # vertical layout
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=main_window
        )
        w.show()
        return
    def get_device(self):
        return main_window.title_bar.combobox.currentText()
    def kill_all(self):
        device = self.get_device()
        if device == '':
            self.show_no_device_error()
        n=0
        for i in self.info['ps'].keys():
            res = run_cmd(f'adb -s {device} shell kill -9 {self.info["ps"][i][0]}')
            n+=1
        main_window.show_info_singal.emit('操作成功', f'尝试停止了{n}个进程')
    def kill_ps(self,num):
        device=self.get_device()
        if device=='':
            self.show_no_device_error()
        res = run_cmd(f'adb -s {device} shell kill -9 {num}')
        if res[0]:
            main_window.show_info_singal.emit('操作成功', res[1])
            return 1
        else:
            main_window.show_error_singal.emit('操作失败', res[1])
            return 0
    def get_ps(self,mode='3'):
        device=self.get_device()
        if device=='':
            self.show_no_device_error()
        res = run(f'adb -s {device} shell ps', shell=True, encoding='utf-8', cwd='./adb/', stdout=PIPE)
        info = res.stdout.split('\n')
        ps_name = compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
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
            if ps_name.findall(name) != []:
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
                    main_window.show_error_singal.emit('操作失败', res[1])
                else:
                    main_window.show_info_singal.emit('操作成功', '')
        save_path = path
        if path == 'choose':
            file = QFileDialog.getExistingDirectory(parent=main_window, caption="选取指定文件夹", directory="C:/")
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
                    main_window.show_error_singal.emit('操作失败',res[1])
                else:
                    main_window.show_info_singal.emit('操作成功', '')
            else:
                self.save_app(package=package,path='../temp/')
                activity=self.get_apk_info(show_func=None,apk_path=f'../temp/{package}.apk')[0]
                if activity=='':
                    main_window.show_error_singal.emit('操作失败', '无法检测应用activity名')
                    return
                res=run_cmd(f'adb -s {device} shell am start -n {package}/{str(activity).replace(package,"")}')
                if not res[0]:
                    main_window.show_error_singal.emit('操作失败',res[1])
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
    def file_delete(self,path,stat='file'):
        self.device=self.get_device()
        res=run_cmd(f'adb -s {self.device} shell rm -{"f" if stat=="file" else "rf"} {path}')
        if res[0]:return 1
        else:return 0
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
                    main_window.show_error_singal.emit('安装错误',res[1])
                    main_window.app_installer.ui.data_text.insertPlainText(f'{self.apk_name}安装失败\n')
                    QApplication.processEvents()
                    return 0
                return 1
            except Exception as e:
                print(e,e.__traceback__.tb_lineno)
                return 0
        def start_thread():
            main_window.app_installer.ui.install_btn.setEnabled(False)
            main_window.app_installer.ui.push_lock_btn.setEnabled(False)
            for i in apk_list:
                self.push_name = path.basename(i)
                self.apk_name = self.push_name.replace("(", "\\(").replace(")", "\\)").replace(" ","\ ")
                stat_tool.setContent(f'正在安装{self.push_name}')
                main_window.app_installer.ui.data_text.insertPlainText(f'{self.push_name}开始安装\n')
                if func == '通用模式':
                    device = self.get_device()
                    try:
                        res_push = run_cmd(['adb', '-s', device, 'push', i, f'/sdcard/{self.push_name}'], check=True)
                        data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,data=res_push)
                        QApplication.processEvents()
                        if not reload_result(res_push,self.push_name):continue
                        pipe = Popen("adb -s " + device + " shell", cwd="./adb/", stdin=PIPE, stdout=PIPE,stderr=PIPE, shell=True,encoding='utf-8')
                        res_num = pipe.communicate("\n" + "pm install-create" + "\n")
                        num = Re_obj.install.findall(str(res_num[0]))
                        if num == []:
                            data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,
                                          data=(0, res_num[1]))
                            reload_result((0,res_num),self.apk_name)
                            continue
                        else:data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,data=(1, res_num[0]))
                        QApplication.processEvents()
                        pipe = Popen("adb -s " + device + " shell", cwd="./adb/", stdin=PIPE, stdout=PIPE, shell=True,stderr=PIPE,
                                     encoding='utf-8')
                        res_ready=pipe.communicate(f"pm install-write {num[0]} force /sdcard/{self.apk_name}")
                        QApplication.processEvents()
                        print(res_ready,res_ready[0]!='')
                        if res_ready[0]!='':
                            data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,data=(1, res_ready[0]))
                        else:
                            data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,data=(0, res_num[1]))
                            reload_result((0,res_ready[1]),self.push_name)
                            continue
                        QApplication.processEvents()
                        pipe = Popen("adb -s " + device + " shell", cwd="./adb/", stdin=PIPE, stdout=PIPE,stderr=PIPE, shell=True,
                                     encoding='utf-8')
                        res_install=pipe.communicate(f'pm install-commit {num[0]}')
                        print(res_install)
                        if res_install[0] != '':
                            data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,
                                          data=(1, res_install[0]))
                        else:
                            data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,
                                          data=(0,res_install[1]))
                            reload_result((0, res_install[1]),self.push_name)
                            continue
                        QApplication.processEvents()
                        main_window.app_installer.ui.data_text.insertPlainText(f'{self.push_name}安装成功\n')
                    except Exception as e:
                        reload_result((0,str(e)),self.push_name)
                elif func=='ROOT模式':
                    device=self.get_device()
                    try:
                        self.apk_name=path.basename(i)
                        res=run_cmd(f'adb -s {device} install -r {i}')
                        data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,
                                      data=res)
                        reload_result(res,self.apk_name)
                        main_window.app_installer.ui.data_text.insertPlainText(f'{self.apk_name}安装成功\n')
                    except Exception as e:
                        reload_result((0,str(e)),self.apk_name)

                elif func=='PM模式':
                    try:
                        device=self.get_device()
                        self.apk_name = path.basename(i)
                        res_push = run_cmd(['adb', '-s', device, 'push', i, f'/sdcard/{self.push_name}'], check=True)
                        data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,
                                      data=res_push)
                        if reload_result(res_push,self.push_name):continue
                        res_install = run_cmd(f'adb -s {device} shell pm install /sdcard/{self.apk_name}')
                        print(res_install)
                        data_inserter(insert_func=main_window.app_installer.ui.data_text.insertPlainText,
                                      data=res_install)
                        reload_result(res_install,self.apk_name)
                        main_window.app_installer.ui.data_text.insertPlainText(f'{self.apk_name}安装成功\n')

                    except Exception as e:
                        reload_result((0,str(e)))
            stat_tool.setState(True)
            stat_tool.setContent('安装任务完成!')
            stat_tool.setTitle('完成!')
            stat_tool.fadeOut()
            stat_tool.deleteLater()
            self.file_delete(path=f'/sdcard/{self.push_name}')
            main_window.app_installer.ui.install_btn.setEnabled(True)
            main_window.app_installer.ui.push_lock_btn.setEnabled(True)
        if self.get_device()=='':
            self.show_no_device_error()
            return
        if apk_list!=[]:
            stat_tool = New_StateToolTip(title='安装中...', content='正在安装', parent=main_window,isclose=False)
            stat_tool.show()
            t=Thread_result(func=start_thread)
            t.start()
    def get_devices(self):  # 获取设备连接device名称
        devices = run_cmd("adb devices")
        devices = Re_obj.device.findall(devices[1])
        choice = self.get_device()
        main_window.title_bar.combobox.clear()
        main_window.title_bar.combobox.addItems(devices)
        if choice in devices:
            main_window.home.ui.label.setText('设备:'+choice)
        elif devices != []:
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
        if DPI[0]:
            res = str(DPI[1]).split("\n")
            if len(res) == 1:
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
        sdcard_all = int(str(sdcard_df[1]).split("\n")[1].split(" ")[5]) / 1024 ** 2
        sdcard_used = int(str(sdcard_df[1]).split("\n")[1].split(" ")[6]) / 1024 ** 2
        root_all = int(str(root_df[1]).split("\n")[1].split(" ")[12]) / 1024 ** 2
        root_used = int(str(root_df[1]).split("\n")[1].split(" ")[13]) / 1024 ** 2
        if sdcard_df[0] and root_df[0]:
            self.info["sdcard"]=[sdcard_used,sdcard_all]
            self.info["root"]=[root_used,root_all]
            return 1, [Re_obj.doc_used.findall(sdcard_df[1])[0], sdcard_used, sdcard_all], [
                Re_obj.doc_used.findall(root_df[1])[0], root_used, root_all]
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
        root = run_cmd("adb -s {} shell su -c id".format(device))
        if root[0] == 0:
            self.info["is_root"] = "--"
            return 0, "--"
        elif "uid=0" in root[1]:
            self.info["is_root"] = "已开启"
            return 1, "已开启"
        else:
            self.info["is_root"] = "未开启"
            return 0, "未开启"

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
    doc_used=compile("(?P<used>\d+)%")
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
class Thread_result(Thread):
    def __init__(self, func,mutex=True,args=()):
        super(Thread_result, self).__init__()
        self.func = func
        self.args = args
        self.mutex=mutex
    def run(self):
        if self.mutex:
            lock=RLock()
            lock.acquire()
            self.result = self.func(*self.args)
            lock.release()
        else:self.result = self.func(*self.args)
    def get_result(self):
        Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None
class Qt_Thread(QThread):
    def __init__(self,func):
        super(Qt_Thread,self).__init__()
        self.func=func
    def run(self):
        self.func()
def run_cmd(code,cwd="./adb/",check=True,encoding="utf-8",thread=(True,True)): # thread=(是否使用多线程，是否开启进程锁)
    def start(code,cwd,check,encoding):
        try:
            res=run(code,cwd=cwd,stdout=PIPE,stderr=PIPE,check=check,encoding=encoding,shell=True)
            return 1,res.stdout.strip("\t\n")
        except SubprocessError as es:
            try:
                return 0,str(res.stderr)
            except Exception as e:
                return 0,str(es)
    if thread[0]:
        t=Thread_result(func=start,mutex=thread[1],args=(code,cwd,check,encoding))
        t.start()
        return t.get_result()
    else:
        return start(code=code,cwd=cwd,check=check,encoding=encoding)
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
                main_window.systemTrayIcon.setToolTip('当前连接:' +str(model))
                version=xtc.get_android_version()[1]
                root=xtc.get_root()[1]
                id=xtc.get_android_id()[1]
                name=xtc.get_name()[1]
                mac=xtc.get_mac()[1]
                brand=xtc.get_brand()[1]
                if xtc.get_device()!=last and xtc.get_device()!="" and brand!="XTC":
                    main_window.message.emit("检测到不是小天才设备","检测到当前设备为"+brand+",并不是小天才手表,这样可能导致部分功能无法使用请悉知","我已知晓","直接无视")
                apk_list = xtc.get_app()[1]
                app_num=len(apk_list)
                if last!=xtc.get_device():
                    main_window.app_manager.ui.set_search(apk_list)
                    main_window.app_manager.ui.ListWidget.clear()
                    main_window.app_manager.ui.ListWidget.addItems(labels=apk_list)
                    ps = xtc.get_ps()
                    main_window.pross_manager.ui.set_search(ps.keys())
                    main_window.pross_manager.ui.ListWidget.clear()
                    main_window.pross_manager.ui.ListWidget.addItems(ps.keys())
                if k==5:
                    k=0
                    used=xtc.get_doc_used()
                    battery=xtc.get_battery()
                    dpi=xtc.setting_density()
                    size=xtc.setting_size()
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
                    main_window.home.ui.label_14.setText("当前屏幕大小: {}".format(size[1]))
                    main_window.home.ui.label_20.setText("默认屏幕大小: {}".format(size[2]))
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
            print(e,e.__traceback__.tb_lineno)
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
def time_out():
    global xtc
    welcome_window.close()
    main_window.setWindowOpacity(1)
    xtc = XTC_func()
    start_worker()
    init_window()
    Thread(target=init_window).start()
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
        res=get("https://lanqinyun.com/s/MbmumeKkui")
        ver=Re_obj.check_update.findall(res.text)
        k=0
        for i in ver:
            v=str(i)
            if float(v)>k:
                k=float(v)
        if k>float(VERSION):
            m = MessageBox(title="有新版本!",
                           content="检测到新版本:小天才专用工具箱V{},快去更新体验最新功能吧!".format(str(k)),
                           parent=main_window)
            m.yesButton.setText("立即更新")
            m.cancelButton.setText("暂不更新")
            if m.exec():
                QDesktopServices.openUrl(QUrl("https://lanqinyun.com/s/MbmumeKkui"))
    except:
        pass

def data_inserter(insert_func,data:tuple):
    time=datetime.now().strftime("%H-%M-%S")
    state='INFO' if data[0] else 'ERROR'
    insert_func(f'[{time}]({state}):{str(data[1]).strip()}\n')

if __name__ == '__main__':
    # enable dpi scale
    if cfg.get(cfg.dpiScale) == "Auto":
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
    main_window.setMinimumWidth(600)
    main_window.titleBar.setMaximumHeight(40)
    timer = QTimer()  # 创建一个定时器
    timer.setSingleShot(True)  # 设置定时器为单次触发
    timer.setInterval(1200)  # 设置定时器间隔为1.2秒（毫秒）
    timer.timeout.connect(time_out)  # 连接定时器的超时信号到窗口的close方法
    timer.start()
    exit(app.exec_())