
import os
import wmi
from win32com.shell import shell as sh
from win32com.shell import shellcon as shcon
import softinfo, bootinfo

class path:
    recent = sh.SHGetSpecialFolderPath(0, shcon.CSIDL_RECENT)
    cookie = sh.SHGetSpecialFolderPath(0, shcon.CSIDL_COOKIES)
    cache  = sh.SHGetSpecialFolderPath(0, shcon.CSIDL_INTERNET_CACHE)
    temp = os.environ['TEMP']

# return count of files, total size
def info(path):
    pass

# clean path with extension name exts
def clean(path, exts = None):
    pass

cim = wmi.WMI()

def soft_info():
    return [i for i in softinfo.all_soft()]

def boot_info():
    return bootinfo.boot_list()

def perf_info(cim = cim):
    info = {}
    for sys in cim.Win32_OperatingSystem():
        total = int(sys.TotalVisibleMemorySize)
        free = int(sys.FreePhysicalMemory)
        avail = total - free
        total = total / 1024 / 1024
        avail = avail / 1024 / 1024
        info['mem_total'] = '%.1f' % total
        info['mem_avail'] = '%.1f' % avail
    for p in cim.Win32_PerfRawData_PerfOS_Processor(Name = '_Total'):
        ps = int(p.PercentProcessorTime)
        ts = int(p.Timestamp_Sys100NS)
        for p in cim.Win32_PerfRawData_PerfOS_Processor(Name = '_Total'):
            cps = int(p.PercentProcessorTime)
            cts = int(p.Timestamp_Sys100NS)
            info['cpu_usage'] = int((1-(cps-ps)/(cts-ts)) * 100)
    return info

def os_info(cim = cim):
    for sys in cim.Win32_OperatingSystem():
        return {
            'name': sys.Caption + ' ' + sys.OSArchitecture,
            'user': os.environ['USERNAME']
        }

def services(cim = cim):
    fields = ['Name', 'Caption', 'State', 'StartMode', 'Started']
    svs = cim.Win32_Service(fields)
    return svs, [{k: getattr(item, k) for k in fields} for item in svs]

def tohuman(size):
    level = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    l = 0
    while size > 1024:
        size /= 1024
        l += 1
    return '%.1f %s' % (size, level[l])

# return directory's count of file, total size
def dirinfo(d):
    size = os.path.getsize(d)
    count = 0
    for path, dirs, files in os.walk(d):
        for file in files:
            p = os.path.join(path, file)
            size += os.path.getsize(p)
            count += 1
    return count, tohuman(size)

def cleaninfo():
    d = {'temp': '临时文件', 'cache': '浏览器缓存',
        'recent': '使用痕迹', 'cookie': 'Cookies'}
    ret = []
    for k, v in d.items():
        p = getattr(path, k)
        c, s = dirinfo(p)
        ret.append({
            'name': v, 'id': k,
            'count': c, 'size': s,
            'path': p
        })
    return ret


if __name__ == '__main__':
    print(cleaninfo())
