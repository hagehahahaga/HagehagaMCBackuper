# HagehagaMCBackuper
第一次进入提示创建配置文件
根据提示输入：
    原存档路径：网易BEMC存档路径，如: 
        C:\Users\Administrator\AppData\Roaming\MinecraftPE_Netease\minecraftWorlds
    备份存档路径：要备份到的存档路径
    检测时间：检测游戏运行的间隔时间，2-3为宜

注：
    程序会创建名为config.ini的配置文件
    路径最后不应加斜杠

更新:
    注意:
        对于v1.1.0及以前版本用户, 请注意配置文件的Config项中有没有:
            LogsToFile = ...
            AutoSave = ...
            AutoSaveTime = ...
        若缺失, 请把缺失项对应修改为:
            LogsToFile = True
            AutoSave = False
            AutoSaveTime = 1
    
    更新只需将下载的程序拖入程序根目录替换文件即可
