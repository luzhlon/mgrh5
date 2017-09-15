
import json
from websocket_server import WebsocketServer

class Handler:
    def _onopen(session):
        pass

    def _onclose(session):
        pass

class RpcSession:
    def __init__(self, wsock, handler):
        self.socket   = wsock        # 与此RpcSession关联的WebSocketSession
        self.handler  = handler      # RPC处理器
        self.callback = {}           # callback与id的关联字典
        self.id       = 1            # id计数器
        wsock._rpcses  = self        # WebSocketSession中与自身相关联的RpcSession

    # 处理call
    def _call(self, id, name, data):
        try:
            fn = getattr(self.handler, name)
            data = fn(self, data)
            data = data if data else []
        except AttributeError:
            data = []
        if id:
            self.retn(id, data)

    # 处理return
    def _retn(self, id, data):
        callback = self._callback4id(id)
        if callback:
            callback(self, data)

    def _handle(self, msg):
        # 解析收到的数据
        msg = json.loads(msg)
        if type(msg[0]) is str:     # call
            name = msg[0]
            id   = msg[1]
            self._call(id, name, msg[2])
        else:                       # return
            id = msg[0]
            self._retn(id, msg[1])

    # 获取callback关联的id
    def _id4callback(self, callback):
        if not callback:
            return 0
        self.callback[self.id] = callback
        id = self.id
        self.id += 1
        return id

    # 获取id关联的callback
    def _callback4id(self, id):
        if id in self.callback:
            callback = self.callback[id]
            del self.callback[id]
            return callback

    # call
    def call(self, name, args = [], callback = None):
        assert type(name) is str
        id = self._id4callback(callback)
        msg = [name, id, args]
        self.socket.send(json.dumps(msg))

    # return
    def retn(self, id, args):
        msg = [id, args]
        self.socket.send(json.dumps(msg))

class RpcServer(WebsocketServer):
    def __init__(self, handler = Handler, **args):
        WebsocketServer.__init__(self, **args)
        self.handler = handler
        self.sessions = {}

    def onopen(self, socket):
        rpcsession = RpcSession(socket, self.handler)
        self.sessions[rpcsession] = 1
        try:
            self.handler._onopen(rpcsession)
        except Exception:
            pass

    def onmessage(self, session, msg):
        session._rpcses._handle(msg)

    def onclose(self, socket):
        rpcsession = socket._rpcses
        try:
            self.handler._onclose(socket._rpcses)
            del self.sessions[rpcsession]
        except Exception:
            pass

    def call(self, name, args):
        for ss in self.sessions.keys():
            ss.call(name, args)

    def start(self):
        self.run_forever()
