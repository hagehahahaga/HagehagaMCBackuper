import psutil
import time
import shutil
from configobj import ConfigObj
import time
from os import system

# 检测程序存在函数


def exefind(exename):
    i = False
    pids = psutil.pids()
    for pid in pids:
        pids = psutil.pids()
        if pid not in pids:
            continue
        if psutil.Process(pid).name() == exename:
            return True
            i = True
            break
    if i == False:
        return False

# 配置配置文件函数


def config_setup():
    conf_ini = "config.ini"
    config = ConfigObj(conf_ini, encoding='UTF8')
    config['Config'] = {}
    config['Config']['OriginalPath'] = input("输入原始存档路径")
    config['Config']['BackupPath'] = input("输入备份存档路径")
    config['Config']['SleepTime'] = input("输入检测频率(s)")
    config.write()


# 程序运行初始化
print("哈嗝哈哈哈嘎编程，用处是在网易基岩版我的世界关闭后自动备份存档至指定位置，搬运注明出处，禁止抄袭")
system("title 哈嗝哈嘎MCBackuper")

# 配置文件
for i in range(1):
    if ConfigObj("config.ini", encoding='UTF8') == {}:
        print("未创建配置文件")
        config_setup()
        break
    elif input("更改配置文件?(T)") == "T":
        config_setup()
print("运行中")

# 检测运行
running1 = False
while True:
    if exefind("Minecraft.Windows.exe") == True:
        running = True
    else:
        running = False
    if running == True:
        if running1 == False:
            print("Game is running...")
            running1 = running
    else:
        if running1 == True:
            shutil.copytree(ConfigObj("config.ini", encoding='UTF8')['Config']['OriginalPath'], ConfigObj("config.ini", encoding='UTF8')['Config']['BackupPath'] + "/" + time.strftime("%Y%m%d%H%M", time.localtime()))
            print("saved to " + ConfigObj("config.ini", encoding='UTF8')['Config']['BackupPath'])
            running1 = running
    time.sleep(int(ConfigObj("config.ini", encoding='UTF8')['Config']['SleepTime']))
