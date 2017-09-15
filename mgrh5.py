
import time, os, core
from queue import Queue
from jsonrpc import RpcServer, Handler
from threading import Thread
from subprocess import Popen
import wmi

Tasks = Queue(10)
OsInfo = None
Server = None

class Task:
    def __init__(self, session, action, args = None):
        self.session = session
        self.action = action
        self.args = args

class Cleaner:
    pass

class Object:
    pass

class MyHandler(Handler):
    def _onopen(ss):
        print('Open session:', ss)
        ss.LAST = Object()
        ss.call('os_info', OsInfo)

    def _onclose(session):
        print('Close session:', session)

    def echo(session, data):
        return data

    def cleaninfo(s, d):
        s.call('cleaninfo', core.cleaninfo())

    def softinfo(s, d):
        data = core.soft_info()
        s.LAST.softinfo = data
        s.call('softinfo', data)

    def bootinfo(s, d):
        data = core.boot_info()
        s.LAST.bootinfo = data
        s.call('bootinfo', data)

    def services(s, d):
        Tasks.put(Task(s, 'services'))

    def open_soft_dir(s, d):
        soft = s.LAST.softinfo[d]
        path = soft.get('InstallLocation', soft.get('UninstallString'))
        if os.path.isdir(path):
            Popen(['rundll32', 'url.dll', 'FileProtocolHandler', path])
        else:
            s.call('popup', '未知的软件路径')

    def uninstall(s, d):
        soft = s.LAST.softinfo[d]
        uninst = soft.get('UninstallString')
        if uninst:
            if uninst[0] != '"':
                uninst = '"%s"' % uninst
            os.system(uninst)
        else:
            s.call('popup', ['无法卸载软件:', soft.DisplayName])

    def clean(s, d):
        path = d

    def enable_boot(s, d):
        pass

    def start_sv(s, d):
        sv = s.LAST.services[d]
        try:
            code = sv.StopService() if sv.Started else sv.StartService()
            s.call('popup', code)
            if code:
                s.call('popup', ['发生错误', code])
                return False
            else:
                s.call('popup', 'Success!')
                return True
        except wmi.x_wmi:
            s.call('popup', '权限异常')
            return False

if __name__ == '__main__':
    Server = RpcServer(port = 8006, handler = MyHandler)
    print('服务器已启动，端口：', 8006)
    Thread(target = lambda: Server.start()).start()

    OsInfo = core.os_info()

    while 1:
        perf = core.perf_info()
        # print(perf)
        Server.call('perf_info', perf)

        while Tasks.qsize():
            task = Tasks.get()
            action = task.action
            session = task.session
            if action == 'services':
                svs, data = core.services()
                session.LAST.services = svs
                session.call('services', data)
            else:
                print('Unsurpported action:', action)

        time.sleep(0.5)
