import inspect
import itertools
import psutil
import time
import shutil
from configobj import ConfigObj
import os
import threading
import updater
import traceback


def printf(
        inpu: str,
        **keys
) -> None:
    """key: 0 - INF,1 - ERR,2 - DEB func"""
    level = keys.get('level', 0)
    func = keys.get('func', inspect.stack()[1][3])
    level_dict = {0: 'INF', 1: 'ERR', 2: 'DEB'}
    inpu = f'{time.strftime("%Y%m%d %H%M%S", time.localtime())} - {func} - [{level_dict[level]}] {inpu}'
    if func not in logs.keys():
        logs[func] = []
    logs[func].append(inpu)
    print(inpu)
    log_write(inpu)


def inputf(
        inpu: str,
        **keys
) -> str:
    func = keys.get('func', inspect.stack()[1][3])
    if func not in logs.keys():
        logs[func] = []
    inpu_formatted = f'{time.strftime("%Y%m%d %H%M%S", time.localtime())} - {func} - [IPU] {inpu}'
    if inpu != '':
        logs[func].append(inpu_formatted)
        inpu_formatted += '\n'
    inpu = input(inpu_formatted)
    logs[func].append(f'{time.strftime("%Y%m%d %H%M%S", time.localtime())} - {func} - [IPU] {inpu}')
    log_write(inpu_formatted + inpu)
    return inpu


def log_write(inpu: str) -> None:
    if bool(config['Config']['LogsToFile']):
        with open(file=log_file, mode='a') as file:
            file.write(inpu + '\n')


def printlog(func: str) -> None:
    if func not in logs:
        return
    print('\n'.join(logs[func]))


def exe_exist(exe_name: str) -> bool:
    """检测程序运行"""
    return exe_name in map(lambda x: x.name(), psutil.process_iter())


def thread_lock():
    """一键上线程锁"""
    if bool(config['Config']['AutoSave']) and not thread_autosave_lock.locked():
        thread_autosave_lock.acquire()
    thread_run_lock.acquire()


def thread_unlock():
    """一键解线程锁"""
    if bool(config['Config']['AutoSave']) and thread_autosave_lock.locked():
        thread_autosave_lock.release()
    thread_run_lock.release()


def save(*tags) -> None:
    """保存存档"""
    tags = ' '.join(map(str, tags))
    shutil.copytree(
        config['Config']['OriginalPath'],
        config['Config']['BackupPath'] +
        os.sep +
        time.strftime("%Y%m%d %H%M", time.localtime()) +
        tags
    )
    printf(f"备份至{config['Config']['BackupPath']}, 标签: {tags}", func='main')


def run() -> None:
    """检测运行"""
    running1 = False
    while not Exit:
        thread_run_lock.acquire()
        running = exe_exist("Minecraft.Windows.exe")
        if running == running1:
            thread_run_lock.release()
            time.sleep(int(config['Config']['SleepTime']))
            continue
        if running:
            printf("游戏运行中...", func='main')
        else:
            save()
        running1 = running
        thread_run_lock.release()


def auto_save():
    """自动保存"""
    while not Exit:
        can_exit_sleep.wait(timeout=int(config['Config']['AutoSave']) * 3600)
        if thread_autosave_lock.acquire(False) and \
                exe_exist("Minecraft.Windows.exe") and \
                bool(config['Config']['AutoSave']):
            save('AutoSave')
        thread_autosave_lock.release()


def config_setup() -> None:
    """配置配置文件"""
    global config
    thread_lock()

    if not config['Config'].get('OriginalPath'):
        os.system("CLS")
        printf("创建配置文件")
        config['Config']['OriginalPath'] = inputf("输入原始存档路径")
        config['Config']['BackupPath'] = inputf("输入备份存档路径")
        config['Config']['SleepTime'] = inputf("输入检测频率(s)")
        config['Config']['Version'] = version
        config['Config']['ChainStart'] = ''
        config.write()
        thread_unlock()
        return

    inpu_dict = dict(
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
                    'str'  # bool
                ),
                (
                    'AutoSave',
                    '回车为否, 反之为自动备份间隔(h)',
                    'str'  # bool, int
                ),
                (
                    'ChainStart',
                    '回车为否, 反之为串联启动路径',
                    'str'  # bool, str
                )
            )
        )
    )
    inpu_dict_len = len(inpu_dict)

    while True:
        os.system("CLS")
        print(
            '输入',
            ', '.join(
                map(
                    lambda x, y: (
                        f'{x} {y}'
                    ),
                    itertools.count(),
                    (
                        '更改原始存档路径',
                        '更改备份存档路径',
                        '更改检测频率(s)',
                        '更改是否输出日志到本地',
                        '更改自动备份配置',
                        '更改串联启动配置',
                        '取消',
                        '确定'
                    )
                )
            )
        )
        printlog('config_setup')

        inpu = inputf('')
        if inpu in inpu_dict:
            try:
                config['Config'][inpu_dict[inpu][0]] = eval(inpu_dict[inpu][2])(
                    inputf(f"当前为 {config['Config'][inpu_dict[inpu][0]]}, 输入{inpu_dict[inpu][1]}"))
            except:
                printf(f'错误:\n{traceback.format_exc()}', level=1)
        if inpu == str(inpu_dict_len):
            config = ConfigObj("config.ini", encoding='UTF8')
            break
        if inpu == str(inpu_dict_len + 1):
            config.write()
            printf('更改成功')
            time.sleep(uisleeptime)
            break

    thread_unlock()


def backups() -> None:
    """管理备份们"""

    def backup(dir: str) -> None:
        """管理备份"""

        worlds_backup = next(os.walk(dir))[1]
        worlds_original = next(os.walk(config["Config"]["OriginalPath"]))[1]
        while True:
            inpu_backup = inputf(
                f'备份{dirlist[inpu]} 含有 {len(worlds_backup)} 个存档, 原存档有 {len(worlds_original)} 个存档, 输入 0 删除, 1 回档, 2 '
                f'展示差异, 3 返回',
                func='backups')
            if inpu_backup == '0':
                shutil.rmtree(dir)
                printf('删除成功', func='backups')
                time.sleep(uisleeptime)
                break

            elif inpu_backup == '1':
                if exe_exist("Minecraft.Windows.exe"):
                    printf('游戏运行中,请关闭游戏再回档', level=1, func='backups')
                    time.sleep(uisleeptime)
                    break

                original_path = config['Config']['OriginalPath'].split(os.sep)
                original_path_name = original_path[-1]
                original_path = os.sep.join(original_path[:-1])
                shutil.rmtree(config['Config']['OriginalPath'])
                shutil.copytree(dir, original_path + "/" + original_path_name)
                printf('回档成功', func='backups')
                time.sleep(uisleeptime)
                break

            elif inpu_backup == '2':
                worlds_backup_max_len = len(max(worlds_backup))
                printf(
                    f'\n\n{"备份存档:".ljust(worlds_backup_max_len - 4)} - 原存档:\n' +
                    '\n'.join(
                        itertools.chain(
                            map(
                                lambda x: f'{x.ljust(worlds_backup_max_len, "-")} - {x}',
                                sorted(set(worlds_backup) & set(worlds_original))
                            ),
                            map(
                                lambda x: f'{x.ljust(worlds_backup_max_len, "-")} - ',
                                sorted(set(worlds_backup) - set(worlds_original))
                            ),
                            map(
                                lambda x: f'{"".ljust(worlds_backup_max_len, "-")} - {x}',
                                sorted(set(worlds_original) - set(worlds_backup))
                            )
                        )
                    ) +
                    '\n',
                    func='backups'
                )

            elif inpu_backup == '3':
                break

    thread_lock()

    while True:
        os.system("CLS")
        print('备份如下:')
        dirlist = dict(zip(itertools.count(), os.listdir(config['Config']['BackupPath'])))
        print(
            '\n'.join(
                map(
                    lambda x: (
                        f'{x} - {dirlist[x]}'
                    ),
                    dirlist
                )
            ),
            f'\n\n当前共有 {len(dirlist)} 个备份, 输入备份相应数字管理, {len(dirlist)} 返回'
        )
        printlog('backups')

        try:
            inpu = int(inputf(''))
        except:
            continue
        if inpu in dirlist:
            backup(config['Config']['BackupPath'] + os.sep + dirlist[inpu])
        elif inpu == len(dirlist):
            break

    thread_unlock()


def main() -> None:
    """主函数"""

    def logs_reset() -> None:
        """重置日志"""
        global logs
        logs = {'main': ['哈嗝哈哈哈嘎编程，能在网易基岩版我的世界关闭后自动备份存档至指定位置',
                         '输入 0 进入设置, 1 立刻保存, 2 管理备份, 3 清除日志, 4 退出']}

    def exit() -> None:
        """退出程序"""
        global Exit
        printf('退出中......请稍等', func='main')
        can_exit_sleep.set()
        Exit = True

    global logs
    global Exit

    os.system("title 哈嗝哈嘎MCBackuper")
    logs_reset()

    if config == {}:
        os.mkdir('.\\logs')
        config['Config'] = {}
        config['Config']['LogsToFile'] = 'True'
        config['Config']['AutoSave'] = ''
        printf('未创建配置文件', level=1, func='config_setup')
        config_setup()

    version_config = list(map(int, config['Config'].get('Version', [])))
    if version != version_config:
        for function_iterated in filter(
            lambda version_iter: version_config < version_iter,
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
        ):
            eval(f'updater.v{"_".join(map(str, function_iterated))}')()
        config.reload()
        config['Config']['Version'] = version
        config.write()

        printf(f'用户文件更新完毕, 程序原版本: {version_config}, 现在版本: {version}')
        input('按回车继续')

    if config['Config']['ChainStart'] and not exe_exist(config['Config']['ChainStart'].split(os.sep)[-1]):
        printf(f'串联启动中, 路径: {config["Config"]["ChainStart"]}')
        os.startfile(config["Config"]["ChainStart"])

    threading.Thread(target=run).start()

    if not bool(config['Config']['AutoSave']):
        thread_autosave_lock.acquire()

    threading.Thread(target=auto_save).start()

    inpu_dict = dict(zip(map(lambda x: str(x), itertools.count()), (config_setup, save, backups, logs_reset, exit)))
    while not Exit:
        os.system("CLS")
        printlog('main')

        inpu = inputf('')
        if inpu in inpu_dict:
            inpu_dict[inpu]()
        elif inpu.find('/') == 0:
            try:
                printf(str(eval(inpu[1:])), level=2)
            except:
                printf(f'错误:\n{traceback.format_exc()}', level=2)


version = [1, 3, 1]
log_file = f'.{os.sep}Logs{os.sep}log - {time.strftime("%Y%m%d %H%M%S", time.localtime())}.txt'
config = ConfigObj("config.ini", encoding='UTF8')
Exit = False
can_exit_sleep = threading.Event()
thread_run_lock = threading.Lock()
thread_autosave_lock = threading.Lock()
uisleeptime = 0.5
logs = {}
main()
