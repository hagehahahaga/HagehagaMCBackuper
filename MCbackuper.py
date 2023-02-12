import atexit
from copy import deepcopy
from itertools import count
import psutil
import time
import shutil
from configobj import ConfigObj
import os
import threading

def printf(inpu:str,func:str,level:int)->None:
    '''0:INF,1:ERR,2:DEB'''
    level_dict={0:'INF',1:'ERR',2:'DEB'}
    inpu='%s - %s - [%s] %s'%(time.strftime("%Y%m%d %H%M%S", time.localtime()),func,level_dict[level],inpu)
    if func not in logs.keys():
        logs[func]=[]
    logs[func].append(inpu)
    print(inpu)

def inputf(inpu:str,func:str)->str:
    if func not in logs.keys():
        logs[func]=[]
    inpu_formarted=('%s - %s - [IPU] %s'%(time.strftime("%Y%m%d %H%M%S", time.localtime()),func,inpu))
    if inpu!='':
        logs[func].append(inpu_formarted)
        inpu_formarted+='\n'
    inpu=input(inpu_formarted)
    logs[func].append('%s - %s - [IPU] %s'%(time.strftime("%Y%m%d %H%M%S", time.localtime()),func,inpu))
    return inpu

def printlog(func):
    if func not in logs:
        return
    print('\n'.join(logs[func]))

def config_setup():
    '''配置配置文件'''
    global mainrun
    global config
    mainrun=False

    if config == {}:
        os.system("CLS")
        printf("创建配置文件",'config_setup',0)
        config['Config'] = {}
        config['Config']['OriginalPath'] = inputf("输入原始存档路径",'config_setup')
        config['Config']['BackupPath'] = inputf("输入备份存档路径",'config_setup')
        config['Config']['SleepTime'] = inputf("输入检测频率(s)",'config_setup')
        config['Config']['AutoSaveLogs'] = True
        config.write()
        mainrun=True
        return

    inpu_dict=dict(zip(map(lambda x:str(x),count()),(('OriginalPath','原始存档路径','str'),('BackupPath','备份存档路径','str'),('SleepTime','检测频率(s)','int'),('AutoSaveLogs','回车为否, 反之为是','bool'))))

    while True:
        os.system("CLS")
        print("输入 0 更改原始存档路径, 1 更改备份存档路径, 2 更改检测频率(s), 3 更改自动保存日志, 4 取消, 5 确定")
        printlog('config_setup')

        inpu=inputf('','config_setup')
        if inpu in inpu_dict:
            try:
                config['Config'][inpu_dict[inpu][0]]=eval(inpu_dict[inpu][2])(inputf("当前为 %s , 输入%s"%(config['Config'][inpu_dict[inpu][0]],inpu_dict[inpu][1]),'config_setup'))
            except Exception as exception:
                printf('错误:%s'%(exception),'config_setup',1)
        elif inpu=='4':
            config=ConfigObj("config.ini", encoding='UTF8')
            break
        elif inpu=='5':
            config.write()
            printf('更改成功','config_setup',0)
            time.sleep(uisleeptime)
            break
    
    mainrun=True

def save():
    '''保存存档'''
    shutil.copytree(config['Config']['OriginalPath'], config['Config']['BackupPath'] + "/" + time.strftime("%Y%m%d %H%M", time.localtime()))
    printf('备份至%s'%(config['Config']['BackupPath']),'main',0)

def exeExist(exename):
    '''检测程序运行'''
    for pid in psutil.pids():
        try:
            if psutil.Process(pid).name() == exename:
                return True
        except:
            return exeExist(exename)
    return False

def run():
    '''检测运行'''
    running1 = False
    while not Exit:
        running = exeExist("Minecraft.Windows.exe")
        if running==running1 or not mainrun:
            time.sleep(int(config['Config']['SleepTime']))
            continue
        if running:
            printf("游戏运行中...",'main',0)
        else:
            save()
        running1 = running

def backups():
    '''管理备份们'''
    def backup(dir):
        '''管理备份'''
        nonlocal inpu
        def DirsCount(dir):
            '''存档计数'''
            Count=0
            for dirs in os.listdir(dir):
                if os.path.isdir(dir+os.sep+dirs):
                    Count+=1
            return Count
        os.system("CLS")

        while True:
            inpu=inputf('备份 %s 含有 %s 个存档, 原存档有 %s 个存档, 输入 0 删除, 1 回档, 2 返回'%(dirlist[inpu],DirsCount(dir),DirsCount(config['Config']['OriginalPath'])),'backups')
            if inpu=='0':
                shutil.rmtree(dir)
                printf('删除成功','backups',0)
                time.sleep(uisleeptime)
                break

            elif inpu=='1':
                if exeExist("Minecraft.Windows.exe"):
                    printf('游戏运行中,请关闭游戏再回档','backups',1)
                    time.sleep(uisleeptime)
                    break

                OriginalPath=config['Config']['OriginalPath']
                OriginalPathName=OriginalPath[-OriginalPath[::-1].find(os.sep):]
                OriginalPath=OriginalPath[:-OriginalPath[::-1].find(os.sep)-1]
                shutil.rmtree(config['Config']['OriginalPath'])
                shutil.copytree(dir , OriginalPath + "/" + OriginalPathName)
                printf('回档成功','backups',0)
                time.sleep(uisleeptime)
                break
            
            elif inpu=='2':
                break
    global mainrun
    mainrun=False

    while True:
        os.system("CLS")
        print('备份如下:')
        dirlist=os.listdir(config['Config']['BackupPath'])
        dirlist=dict(zip(count(),dirlist))
        print('\n'.join(map(lambda x:'%s - %s'%(x,dirlist[x]),dirlist)))
        print('\n')

        print('当前共有 %s 个备份, 输入备份相应数字管理, %s 返回'%(len(dirlist),len(dirlist)))
        printlog('backups')

        try:inpu=int(inputf('','backups'))
        except:continue
        if inpu in dirlist.keys():
            backup(config['Config']['BackupPath'] + os.sep + dirlist[inpu])
        elif inpu==len(dirlist):
            break

    mainrun=True

@atexit.register
def exit_save():
    '''退出保护'''
    if bool(config['Config']['AutoSaveLogs'])==False:
        return
    logs_export()

def logs_export():
    '''导出日志'''
    def sort_key(elem:str)->int:
        return int(elem[0:8]+elem[9:14])

    if not bool(config['Config']['AutoSaveLogs']):
        return

    printf('导出日志中......','main',0)
    logs_local=deepcopy(logs)
    logs_local['main']=logs_local['main'][2:]
    logs_local_thin=[]
    for log in logs_local.values():
        logs_local_thin.extend(log)
    logs_local=logs_local_thin
    del logs_local_thin
    logs_local.sort(key=sort_key)

    with open('log - '+time.strftime("%Y%m%d %H%M%S", time.localtime())+'.txt','w') as file:
        file.write('\n'.join(logs_local))

def main():
    '''主函数'''
    def logs_reset():
        '''重置日志'''
        global logs
        logs={}
        logs['main']=['哈嗝哈哈哈嘎编程，能在网易基岩版我的世界关闭后自动备份存档至指定位置',\
            '输入 0 进入设置, 1 立刻保存, 2 管理备份, 3 清除日志, 4 导出日志, 5 退出']

    def exit():
        '''退出程序'''
        global Exit
        printf('退出中......请稍等','main',0)
        Exit=True

    global logs
    global Exit
    os.system("title 哈嗝哈嘎MCBackuper")
    logs_reset()

    if config == {}:
        printf('未创建配置文件','main',1)
        config_setup()
    
    Thread_run=threading.Thread(target = run)
    Thread_run.start()
    inpu_dict=dict(zip(map(lambda x:str(x),count()),(config_setup,save,backups,logs_reset,logs_export,exit)))
    while not Exit:
        os.system("CLS")
        printlog('main')

        inpu=inputf('','main')
        if inpu in inpu_dict:
            inpu_dict[inpu]()
        elif inpu.find('/')==0:
            try:
                printf(str(eval(inpu[1:])),'main',2)
            except Exception as error:
                printf('错误: %s'%(error),'main',2)

config=ConfigObj("config.ini", encoding='UTF8')
Exit=False
mainrun=True
uisleeptime=0.5
main()