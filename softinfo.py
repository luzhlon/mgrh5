
from winreg import *
import platform
import regaux

soft_fields = {
    '_key'            : '子键',
    'DisplayName'     : '软件名称',
    'DisplayVersion'  : '版本号',
    'InstallLocation' : '安装位置',
    'Publisher'       : '发行商',
    'UninstallString' : '卸载命令',
    'InstallDate'     : '安装日期'
}
# 是否是64位系统
def is_64():
    return platform.architecture()[0] == '64bit'
# 返回所有的软件卸载信息
def all_soft():
    subKey = 'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall' \
            if is_64() else 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
    with OpenKeyEx(HKEY_LOCAL_MACHINE, subKey) as result:
        for key in regaux.keys(result):
            with OpenKeyEx(result, key) as s:
                info = { '_key': key }
                for field in soft_fields:
                    try: info[field] = QueryValueEx(s, field)[0]
                    except: pass
                if 'DisplayName' in info:
                    yield info
                else:
                    continue

if __name__ == "__main__":
    for info in all_soft():
        print(info['DisplayName'], ':')
        del info['DisplayName']
        for (k, v) in info.items():
            print('\t', soft_fields[k], ':', v)
