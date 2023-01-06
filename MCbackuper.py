import psutil
import time
import shutil
from configobj import ConfigObj
import os
import threading

def printf(inpu,func):
    logs[func].append(inpu)
    print(inpu)

def inputf(inpu,func):
    if func not in logs.keys():
        logs[func]=[]
    if inpu!='':
        logs[func].append(inpu)
        inpu+='\n'
    inpu=input(inpu)
    logs[func].append(inpu)
    return inpu

def config_setup(Create):
    '''配置配置文件'''
    global mainrun
    global config
    mainrun=False

    if Create==True:
        os.system("CLS")
        printf("创建配置文件",'config_setup')
        config['Config'] = {}
        config['Config']['OriginalPath'] = inputf("输入原始存档路径",'config_setup')
        config['Config']['BackupPath'] = inputf("输入备份存档路径",'config_setup')
        config['Config']['SleepTime'] = inputf("输入检测频率(s)",'config_setup')
        config.write()
    else:
        while True:
            os.system("CLS")
            print("输入 0 更改原始存档路径, 1 更改备份存档路径, 2 更改检测频率(s), 3 取消, 4 确定")
            if 'config_setup' in logs.keys():
                for log in logs['config_setup']:
                    print(log)

            inpu=inputf('','config_setup')
            if inpu=='0':
                config['Config']['OriginalPath'] = inputf("当前为 %s , 输入原始存档路径"%(config['Config']['OriginalPath']),'config_setup')
                time.sleep(uisleeptime)
            elif inpu=='1':
                config['Config']['BackupPath'] = inputf("当前为 %s , 输入备份存档路径"%(config['Config']['BackupPath']),'config_setup')
                time.sleep(uisleeptime)
            elif inpu=='2':
                config['Config']['SleepTime'] = inputf("当前为 %s , 输入检测频率(s)"%(config['Config']['SleepTime']),'config_setup')
                time.sleep(uisleeptime)
            elif inpu=='3':
                config=ConfigObj("config.ini", encoding='UTF8')
                break
            elif inpu=='4':
                config.write()
                printf('更改成功','config_setup')
                time.sleep(uisleeptime)
                break
    
    mainrun=True

def save():
    '''保存存档'''
    shutil.copytree(config['Config']['OriginalPath'], config['Config']['BackupPath'] + "/" + time.strftime("%Y%m%d %H%M", time.localtime()))
    printf('在%s保存至%s'%(time.strftime("%Y%m%d %H%M", time.localtime()),config['Config']['BackupPath']),'main')

def run():
    '''检测运行'''
    def exefind(exename):
        '''检测程序存在'''
        pids = psutil.pids()
        for pid in pids:
            try:
                if psutil.Process(pid).name() == exename:
                    return True
            except:
                pass
        return False

    running1 = False
    while True:
        if Exit==True:
            break
        if mainrun==True:
            if exefind("Minecraft.Windows.exe") == True:
                    running = True
            else:
                running = False
            if running == True and running1 == False:
                printf("游戏运行中...",'main')
                running1 = running
            elif running == False and running1 == True:
                save()
                running1 = running
        time.sleep(int(config['Config']['SleepTime']))

def backups():
    '''管理备份们'''
    global mainrun
    mainrun=False
    def DirsCount(dir):
        '''存档计数'''
        Count=0
        for dirs in os.listdir(dir):
            if os.path.isdir(dir+os.sep+dirs)==True:
                Count+=1
        return Count

    def backup(dir):
        '''管理备份'''
        while True:
            os.system("CLS")

            inpu=input('这个备份含有 %s 个存档, 原存档有 %s 个存档, 输入 0 删除, 1 回档, 2 返回\n'%(DirsCount(dir),DirsCount(config['Config']['OriginalPath'])))
            if inpu=='0':
                shutil.rmtree(dir)
                print('删除成功')
                time.sleep(uisleeptime)
                break

            elif inpu=='1':
                OriginalPath=config['Config']['OriginalPath']
                OriginalPathName=''
                for i in OriginalPath[::-1]:
                    OriginalPath=OriginalPath[:-1]
                    if i ==os.sep:
                        break
                    OriginalPathName+=i
                OriginalPathName=OriginalPathName[::-1]
                shutil.rmtree(config['Config']['OriginalPath'])
                shutil.copytree(dir , OriginalPath + "/" + OriginalPathName)
                print('回档成功')
                time.sleep(uisleeptime)
                break

            elif inpu=='2':
                break

    while True:
        os.system("CLS")
        print('备份如下:')
        dirlist=os.listdir(config['Config']['BackupPath'])
        dirlist={str(i):dirlist[i] for i in range(len(dirlist))}
        for dir in dirlist.keys():
            print('%s-%s'%(dir,dirlist[dir]))
        print('\n')

        print('当前共有 %s 个备份, 输入备份相应数字管理, %s 返回'%(len(dirlist),len(dirlist)))
        if 'backups' in logs.keys():
            for log in logs['backups']:
                print(log)
        inpu=inputf('','backups')
        if inpu in dirlist.keys():
            backup(config['Config']['BackupPath'] + os.sep + dirlist[inpu])
        elif inpu==str(len(dirlist)):
            break

    mainrun=True

def main():
    '''主函数'''
    # 程序运行初始化
    global Exit
    os.system("title 哈嗝哈嘎MCBackuper")

    # 配置文件
    if config == {}:
        print("未创建配置文件")
        config_setup(True)
    
    threading.Thread(target = run).start()
    print("运行中")
    while True:
        os.system("CLS")
        for log in logs['main']:
            print(log)

        inpu=inputf('','main')
        if inpu=="0":
            config_setup(False)
        elif inpu=='1':
            save()
            time.sleep(uisleeptime)
        elif inpu=='2':
            backups()
        elif inpu=='3':
            print('退出中......请稍等')
            Exit=True
            break
        elif inpu.find('/')==0:
            try:
                printf(str(eval(inpu[1:])),'main')
            except:
                printf('Error','main')

config=ConfigObj("config.ini", encoding='UTF8')
Exit=False
mainrun=True
uisleeptime=0.5
logs={}
logs['main']=['哈嗝哈哈哈嘎编程，能在网易基岩版我的世界关闭后自动备份存档至指定位置','输入 0 进入设置, 1 立刻保存, 2 管理备份, 3 退出']
main()