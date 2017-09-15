var client, handler;

var G = {
    os_username: '--', os_name: '--',
    cpu_usage: '--',
    mem_avail: '0', mem_total: '0',
    LOG: '',
    net_state: '服务器未连接',
    netstate_label: 'label-danger',
    label_class: 'label',
    server_ip: 'localhost', server_port: 8006,
    bgimg_url: '',
    softlist: [],
    bootlist: [],
    servicelist: [],
    cleanlist: [],
    on_connect: function(e) {
        if (client) client.close();
        handler.CONNECT();
    },
    on_bgimg: function (e) {
        document.body.style.backgroundImage =
            'url(' + G.bgimg_url + ')';
    }
};

new Vue({el: '#topbar', data: G});
new Vue({el: '#statusbar', data: G});

new Vue({el: '#softlist', data: G});
new Vue({el: '#bootlist', data: G});
new Vue({el: '#servicelist', data: G});
new Vue({el: '#cleanlist', data: G});

new Vue({el: '#setting-modal', data: G});

function LOG() {
    var args = Array.prototype.slice.call(arguments);
    G.LOG = args.join(' ');
    console.log(arguments);
}

handler = {
    CONNECT: function() {
        var ip = G.server_ip;
        var port = G.server_port;
        var url = 'ws://' + ip;
        if (port) url += ':' + port;
        client = new Session(url, this);
    },
    _onopen : function (session) {
        G.net_state = '已连接至服务器'; G.netstate_label = 'label-success';
        $('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
            var self = $(e.target);
            self.css('background-color', 'rgba(51,122,183,0.5)').siblings()
                .css('background-color', '');
            switch (self.text()) {
            case '软件管理':
                if (G.softlist.length == 0) {
                    G.softlist = [{DisplayName: '加载中 ...'}];
                    session.call('softinfo');
                }
                break;
            case '服务管理':
                if (G.servicelist.length == 0) {
                    G.servicelist = [{Name: '加载中 ...'}];
                    session.call('services');
                }
                break;
            case '启动管理':
                if (G.bootlist.length == 0) {
                    G.bootlist = [['加载中 ...']];
                    session.call('bootinfo');
                }
                break;
            case '垃圾清理':
                if (G.cleanlist.length == 0) {
                    G.cleanlist = [{name: '正在扫描中 ...'}];
                    session.call('cleaninfo');
                }
                break;
            }
        });
        $('#left-list a:first').tab('show');
    },
    _onerror : function (session) { LOG('Error:', session); },
    _onclose : function (session) {
        G.net_state = '服务器未连接'; G.netstate_label = 'label-danger';
    },
    echo : function (s, d) { return d; },
    log: function(s, d) { LOG(d); },
    perf_info: function (s, d) {
        G.mem_total = d.mem_total;
        G.mem_avail = d.mem_avail;
        G.cpu_usage = d.cpu_usage;
    },
    popup: function (s, d) {
        if (typeof(d) != 'string')
            d = d.toString();
        $('#popup').attr('data-content', d).popover('show');
        setTimeout(function() { $('#popup').popover('hide'); }, 1000);
    },
    os_info: function (s, d) {
        G.os_username = d.user;
        G.os_name = d.name;
    },
    softinfo: function (s, d) { G.softlist = d; },
    bootinfo: function(s, d) { G.bootlist = d; },
    cleaninfo: function(s, d) { G.cleanlist = d; },
    services: function(s, d) { G.servicelist = d; }
};

// 重新计算页面高度
window.onresize = function() {
    $('body, html').css('height', window.innerHeight);
};
window.onresize();

// Connect to server
handler.CONNECT();

// Get a index of row in a table
function getrow(node) {
    if (node.tagName == 'TR')
        return node;
    return getrow(node.parentNode);
}

function rowindex(node) {
    return getrow(node).rowIndex - 1;
}

$('#softlist').on('click', '.displayname', function(e) {
    client.call('open_soft_dir', rowindex(e.target));
});

$('#softlist').on('click', '.action-uninstall', function(e) {
    client.call('uninstall', rowindex(e.target));
});

$('#servicelist').on('click', '.clickable', function(e) {
    var self = $(e.target);
    client.call('start_sv', rowindex(e.target), function(s, d) {
        if (d[0])
            self.text(self.text() == '启动'? '停止': '启动');
    });
});
// Clean
$('#cleanlist').on('click', '.clickable', function(e) {
    client.call('clean', rowindex(e.target));
});
// Clean all
$('#clean-pane').on('click', 'button.btn', function(e) {
    var self = $(e.target);
    if (self.hasClass('btn-primary'))
        self.removeClass('btn-primary')
            .addClass('btn-danger')
            .text('停止清理');
    else
        self.removeClass('btn-danger')
            .addClass('btn-primary')
            .text('清理全部');
    // client.call('clean', rowindex(e.target));
});

$('#bootlist').on('click', '.clickable', function(e) {
    var self = $(e.target);
    self.text(self.text() == '启用' ? '禁用': '启用');
    // client.call('enable_boot', rowindex(e.target));
});
