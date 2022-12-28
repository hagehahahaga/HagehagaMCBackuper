import psutil
import time
import shutil
from configobj import ConfigObj
from os import system
import threading

def exefind(exename):
    # 检测程序存在函数
    i = False
    pids = psutil.pids()
    for pid in pids:
        pids = psutil.pids()
        if pid not in pids:
            continue
        if psutil.Process(pid).name() == exename:
            i = True
            return True
    if i == False:
        return False

def config_setup(Create):
    # 配置配置文件函数
    global mainrun
    mainrun=False
    system("CLS")

    conf_ini = "config.ini"
    config = ConfigObj(conf_ini, encoding='UTF8')
    if Create==True:
        print("创建配置文件")
        config['Config'] = {}
        config['Config']['OriginalPath'] = input("输入原始存档路径")
        config['Config']['BackupPath'] = input("输入备份存档路径")
        config['Config']['SleepTime'] = input("输入检测频率(s)")
        config.write()
    else:
        while True:
            inpu=input("输入 0 更改原始存档路径, 1 更改备份存档路径, 2 更改检测频率(s), 3 返回")
            if inpu=='0':
                config['Config']['OriginalPath'] = input("输入原始存档路径")
            elif inpu=='1':
                config['Config']['BackupPath'] = input("输入备份存档路径")
            elif inpu=='2':
                config['Config']['SleepTime'] = input("输入检测频率(s)")
            elif inpu=='3':
                break
    
    mainrun=True

def save():
    shutil.copytree(ConfigObj("config.ini", encoding='UTF8')['Config']['OriginalPath'], ConfigObj("config.ini", encoding='UTF8')['Config']['BackupPath'] + "/" + time.strftime("%Y%m%d %H%M", time.localtime()))
    print("Saved to " + ConfigObj("config.ini", encoding='UTF8')['Config']['BackupPath'] + " at " + time.strftime("%Y%m%d %H%M", time.localtime()))

def run():
    running1 = False
    # 检测运行
    while True:
        if Exit==True:
            break
        if mainrun==True:
            if exefind("Minecraft.Windows.exe") == True:
                    running = True
            else:
                running = False
            if running == True:
                if running1 == False:
                    print("Game is running...")
                    running1 = running
            elif running1 == True:
                save()
                running1 = running
            time.sleep(int(ConfigObj("config.ini", encoding='UTF8')['Config']['SleepTime']))

def main():
    # 程序运行初始化
    global Exit
    system("title 哈嗝哈嘎MCBackuper")

    # 配置文件
    if ConfigObj("config.ini", encoding='UTF8') == {}:
        print("未创建配置文件")
        config_setup(True)
    
    threading.Thread(target = run).start()
    print("运行中")
    while True:
        system("CLS")
        print("哈嗝哈哈哈嘎编程，用处是在网易基岩版我的世界关闭后自动备份存档至指定位置")
        inpu=input('输入 0 更改配置文件, 1 立刻保存, 2 退出')
        if inpu=="0":
            config_setup(False)
        elif inpu=='1':
            save()
        elif inpu=='2':
            print('退出中......请稍等')
            Exit=True
            break

Exit=False
mainrun=True
main()