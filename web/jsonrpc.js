
function Session (url, handler) {
    var socket = new WebSocket(url);
    var self = this;
    socket.onopen = function (event) {
        handler._onopen(self);
    }
    socket.onmessage = function (event) {
        var data = JSON.parse(event.data);
        self._handle(data);
    }
    socket.onerror = function (event) {
        handler._onerror(self);
    }
    socket.onclose = function (event) {
        handler._onclose(self);
    }
    socket.session = this;
    this.socket = socket;           // Session关联的WebSocket
    this.handler = handler;         // Session的处理器
    this.id = 1;                    // id计数器
    this.callback = {};             // id callback 关联表
    return this;
}
Session.prototype.close = function () {
    this.socket.close();
}
// 通过callback获取id
Session.prototype._id4callback = function (callback) {
    if (callback) {
        this.callback[this.id] = callback;
        return this.id++;
    }
    return null;
}
// 通过id获取callback
Session.prototype._callback4id = function (id) {
    var callback = this.callback[id];
    if (callback) {
        delete this.callback[id];
        return callback;
    }
    return null;
}
// 处理数据包
Session.prototype._handle = function (data) {
    if (typeof data[0] == 'string') {
        var name = data[0];
        var id = data[1];
        this._call(id, name, data[2]);
    } else {
        var id = data[0];
        this._retn(id, data[1]);
    }
}
// 处理call
Session.prototype._call = function (id, name, data) {
    var fn = this.handler[name];
    var ret = null;
    if (fn) {
        ret = fn(self, data);
        if (!data) data = null;
    }
    if (id)
        this.retn(id, ret);
}
// 处理return
Session.prototype._retn = function (id, data) {
    var callback = this._callback4id(id);
    if (callback)
        callback(this, data);
}
// call
Session.prototype.call = function (name, args, callback) {
    var id = this._id4callback(callback);
    var msg = [name, id, args];
    this.socket.send(JSON.stringify(msg));
}
// return
Session.prototype.retn = function (id, args) {
    var msg = [id, args];
    this.socket.send(JSON.stringify(msg));
}
