from winreg import *
import regaux

key_user_boot = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
key_all_boot = "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run"

# 用户所有的启动项
def all_boot_user():
    global key_user_boot

    with OpenKeyEx(HKEY_CURRENT_USER, key_user_boot) as result:
        for name, value, type in regaux.values(result):
            yield (name, value)
            CloseKey(result)

# 系统所有的启动项
def all_boot_machine():
    global key_all_boot

    with OpenKeyEx(HKEY_LOCAL_MACHINE, key_all_boot) as result:
        for name, value, type in regaux.values(result):
            yield (name, value)
            # 所有的启动项

def boot_list():
    l = [i for i in all_boot_user()] + [i for i in all_boot_machine()]
    return l

if __name__ == "__main__":
    print(boot_list())
