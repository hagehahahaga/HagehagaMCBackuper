import shutil
import os
from configobj import ConfigObj


def v1_2_0():
    os.mkdir('logs')
    list(  # 日志文件移入logs文件夹
        map(
            lambda file: (
                shutil.move(
                    file,
                    f'logs{os.sep}{file}'
                )
            ),
            filter(
                lambda file: (
                        file.startswith('log')
                        and
                        file.endswith('txt')
                ),
                next(os.walk('.'))[2]
            )
        )
    )
    print('日志文件已移入文件夹"logs"')


def v1_3_0():
    config = ConfigObj("config.ini", encoding='UTF8')
    config['Config']['ChainStart'] = ''
    if config['Config'].get('AutoSaveTime'):
        config['Config']['AutoSave'] = config['Config']['AutoSaveTime']
    del config['Config']['AutoSaveTime']
    config.write()
