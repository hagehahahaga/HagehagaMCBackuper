import shutil
import os

def v1_1_1():
    os.mkdir('logs')
    list(#日志文件移入loga文件夹
        map(
            lambda file:(
                shutil.move(
                    file,
                    f'logs{os.sep}{file}'
                )
            ),
            filter(
                lambda file:(
                    file.startswith('log')
                    and
                    file.endswith('txt')
                ),
                next(os.walk('.'))[2]
            )
        )
    )
    print('日志文件已移入文件夹"logs"')
    

