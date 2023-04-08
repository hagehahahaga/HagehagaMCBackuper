import itertools
import psutil
import time
import shutil
from configobj import ConfigObj
import os
import threading
import updater

def printf(
        inpu: str,
        func: str,
        level:int
        ) -> None:
    '''0:INF,1:ERR,2:DEB'''
    level_dict={0:'INF',1:'ERR',2:'DEB'}
    inpu=f'{time.strftime("%Y%m%d %H%M%S", time.localtime())} - {func} - [{level_dict[level]}] {inpu}'
    if func not in logs.keys():
        logs[func]=[]
    logs[func].append(inpu)
    print(inpu)
    if bool(config['Config']['LogsToFile']):
        log_write(inpu)

def inputf(
        inpu: str,
        func: str
        ) -> str:
    if func not in logs.keys():
        logs[func]=[]
    inpu_formarted=f'{time.strftime("%Y%m%d %H%M%S", time.localtime())} - {func} - [IPU] {inpu}'
    if inpu!='':
        logs[func].append(inpu_formarted)
        inpu_formarted+='\n'
    inpu=input(inpu_formarted)
    logs[func].append(f'{time.strftime("%Y%m%d %H%M%S", time.localtime())} - {func} - [IPU] {inpu}')
    if bool(config['Config']['LogsToFile']):
        log_write(inpu_formarted+inpu)
    return inpu

def log_write(
        input:str
        ) -> None:
    with open(file=log_file,mode='a') as file:
        file.write(input+'\n')

def printlog(
        func:str
        ) -> None:
    if func not in logs:
        return
    print('\n'.join(logs[func]))

def config_setup() -> None:
    '''配置配置文件'''
    global config
    thread_lock()

    if not config['Config'].get('OriginalPath'):
        os.system("CLS")
        printf("创建配置文件",'config_setup',0)
        config['Config']['OriginalPath'] = inputf("输入原始存档路径",'config_setup')
        config['Config']['BackupPath'] = inputf("输入备份存档路径",'config_setup')
        config['Config']['SleepTime'] = inputf("输入检测频率(s)",'config_setup')
        config['Config']['AutoSaveTime'] = '1'
        config['Config']['Version'] = version
        config.write()
        thread_unlock()
        return

    inpu_dict=dict(
        zip(
            map(
                str,
                itertools.count()
            ),
            (
                (
                    'OriginalPath',
                    '原始存档路径',
                    'str'
                ),
                (
                    'BackupPath',
                    '备份存档路径',
                    'str'
                ),
                (
                    'SleepTime',
                    '检测频率(s)',
                    'int'
                ),
                (
                    'LogsToFile',
                    '回车为否, 反之为是',
                    'bool'
                ),
                (
                    'AutoSave',
                    '回车为否, 反之为是',
                    'bool'
                ),
                (
                    'AutoSaveTime',
                    '自动备份间隔(h)',
                    'int'
                )
            )
        )
    )
    inpu_dict_len=len(inpu_dict)

    while True:
        os.system("CLS")
        print(
            '输入',
            ', '.join(
                map(
                    lambda x, y:(
                        f'{x} {y}'
                    ),
                    itertools.count(),
                    (
                        '更改原始存档路径',
                        '更改备份存档路径',
                        '更改检测频率(s)',
                        '更改是否输出日志到本地',
                        '更改是否开启自动备份',
                        '更改自动备份间隔(h)',
                        '取消',
                        '确定'
                    )
                )
            )
        )
        printlog('config_setup')

        inpu=inputf('','config_setup')
        if inpu in inpu_dict:
            try:
                config ['Config'] [inpu_dict [inpu] [0]] = eval(inpu_dict [inpu] [2]) (inputf(f"当前为 {config ['Config'] [inpu_dict [inpu] [0]]}, 输入{inpu_dict [inpu] [1]}",'config_setup'))
            except Exception as exception:
                printf(f'错误: {exception}','config_setup',1)
        if inpu==str(inpu_dict_len):
            config=ConfigObj("config.ini", encoding='UTF8')
            break
        if inpu==str(inpu_dict_len+1):
            config.write()
            printf('更改成功','config_setup',0)
            time.sleep(uisleeptime)
            break
    
    thread_unlock()

def save(*tags) -> None:
    '''保存存档'''
    tags=' '.join(map(str,tags))
    shutil.copytree(
        config['Config']['OriginalPath'],
        config['Config']['BackupPath'] +
        os.sep +
        time.strftime("%Y%m%d %H%M", time.localtime()) +
        tags
    )
    printf(f"备份至{config['Config']['BackupPath']}, 标签: {tags}",'main',0)

def exeExist(exename:str) -> bool:
    '''检测程序运行'''
    return exename in map(lambda x:x.name(),psutil.process_iter())

def run() -> None:
    '''检测运行'''
    running1 = False
    while not Exit:
        thread_run_lock.acquire()
        running = exeExist("Minecraft.Windows.exe")
        if running==running1:
            thread_run_lock.release()
            time.sleep(int(config['Config']['SleepTime']))
            continue
        if running:
            printf("游戏运行中...",'main',0)
        else:
            save()
        running1 = running
        thread_run_lock.release()

def backups() -> None:
    '''管理备份们'''
    def backup(dir:str) -> None:
        '''管理备份'''
        nonlocal inpu
        def DirsCount(dir:str) -> int:
            '''存档计数'''
            return next(os.walk(dir))[1]
        os.system("CLS")

        while True:
            inpu=inputf(f'备份{dirlist[inpu]} 含有 {DirsCount(dir)} 个存档, 原存档有 {DirsCount(config["Config"]["OriginalPath"])} 个存档, 输入 0 删除, 1 回档, 2 返回','backups')
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

    thread_lock()

    while True:
        os.system("CLS")
        print('备份如下:')
        dirlist=os.listdir(config['Config']['BackupPath'])
        dirlist=dict(zip(itertools.count(),dirlist))
        print(
            '\n'.join(
                map(
                    lambda x:(
                        f'{x} - {dirlist[x]}'
                    ),
                    dirlist
                )
            ),
            f'\n\n当前共有 {len(dirlist)} 个备份, 输入备份相应数字管理, {len(dirlist)} 返回'
        )
        printlog('backups')

        try:inpu=int(inputf('','backups'))
        except:continue
        if inpu in dirlist:
            backup(config['Config']['BackupPath'] + os.sep + dirlist[inpu])
        elif inpu==len(dirlist):
            break

    thread_unlock()

def auto_save():
    '''自动保存'''
    while not Exit:
        can_exit_sleep(int(config['Config']['AutoSaveTime'])*3600)
        if thread_autosave_lock.acquire(0) and exeExist("Minecraft.Windows.exe"):
            save('AutoSave')
        thread_autosave_lock.release()

def thread_lock():
    '''一键上线程锁'''
    if bool(config['Config']['AutoSave']):
        try:thread_autosave_lock.acquire()
        except:...
    thread_run_lock.acquire()

def thread_unlock():
    '''一键解线程锁'''
    if bool(config['Config']['AutoSave']):
        try:thread_autosave_lock.release()
        except:...
    thread_run_lock.release()

def can_exit_sleep(sleep_time: int) -> None:
    '''由Exit布尔值控制退出的sleep'''
    while not Exit and sleep_time > 0:
        time.sleep(1)
        sleep_time-=1

def main() -> None:
    '''主函数'''
    def logs_reset() -> None:
        '''重置日志'''
        global logs
        logs={}
        logs['main']=['哈嗝哈哈哈嘎编程，能在网易基岩版我的世界关闭后自动备份存档至指定位置',
            '输入 0 进入设置, 1 立刻保存, 2 管理备份, 3 清除日志, 4 退出']

    def exit() -> None:
        '''退出程序'''
        global Exit
        printf('退出中......请稍等','main',0)
        Exit=True

    global logs
    global Exit

    os.system("title 哈嗝哈嘎MCBackuper")
    logs_reset()

    if config == {}:
        os.mkdir('.\logs')
        config['Config'] = {}
        config['Config']['LogsToFile'] = 'True'
        config['Config']['AutoSave'] = 'False'
        printf('未创建配置文件','config_setup',0)
        config_setup()

    version_config=list(map(int,config['Config'].get('Version',[])))
    if version != version_config:
        list(
            map(
                lambda x: eval(f'updater.v{"_".join(map(str,x))}')(),
                filter(
                    lambda version: version_config < version,
                    sorted(
                        map(
                            lambda x: list(
                                map(
                                    int,
                                    x[1:].split('_')
                                )
                            ),
                            filter(
                                lambda x: x.startswith('v'),
                                dir(updater)
                            )
                        )
                    )
                )
            )
        )
        config['Config']['Version']=version
        config.write()

        printf(f'用户文件更新完毕, 程序原版本: {version_config}, 现在版本: {version}','main',0)
        input('按回车继续')

    threading.Thread(target = run).start()

    if not bool(config['Config']['AutoSave']):
        thread_autosave_lock.acquire()
    
    threading.Thread(target = auto_save).start()

    inpu_dict=dict(zip(map(lambda x:str(x),itertools.count()),(config_setup,save,backups,logs_reset,exit)))
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

version              = [1,2,0]
log_file             = f'.{os.sep}Logs{os.sep}log - {time.strftime("%Y%m%d %H%M%S", time.localtime())}.txt'
config               = ConfigObj("config.ini", encoding='UTF8')
Exit                 = False
thread_run_lock      = threading.Lock()
thread_autosave_lock = threading.Lock()
uisleeptime          = 0.5
main()