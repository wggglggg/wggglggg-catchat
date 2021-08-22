$(document).ready(function () {
    const ENTER_KEY = 13;
    const popupLoading = '<i class="notched circle circle loading icon green"></i>Loading...';

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            }
        }
    });

    // 点击弹出右sidebar
    function activateSemantics() {
        $('.ui.checkbox').checkbox();

        $('#toggle-sidebar').on('click', function () {
           $('.menu.sidebar').sidebar('setting', 'transition', 'overlay').sidebar('toggle');
        });

        // 缓冲中显示 的消息


        $('.pop-card').popup({
            inline: true,
            on: 'hover',
            hoverable: true,
            html: popupLoading,
            delay: {
                show: 200,
                hide: 200
            },
            onShow: function () {
                let popup = this;
                popup.html(popupLoading);
                $.get({
                    url: $(popup).prev().data('href')
                }).done(function (data) {
                    popup.html(data)
                }).fail(function () {
                    popup.html('Failed to load profile')
                });
            }
        });


    }

    function scrollToBottom() {
        let $messages = $('.messages');
        $messages.scrollTop($messages[0].scrollHeight);
        // $messages会返回一个对象, 这个对象中有一个key为0, $messages[0]会拿到对你是的value, 里面有一项scrollHeight值
        /*  r.fn.init [div.messages, prevObject: r.fn.init(1)]
                0:
                    div.messages
                    accessKey: ""
                    align: ""
                    ariaAtomic: null
                    ariaAutoComplete: null
                    ariaBusy: null
                    ariaChecked: null
                    ariaColCount: null
                    ....
                    scrollHeight: 27320
                    scrollLeft: 0
                    scrollTop: 26755.333984375
                    scrollWidth: 1515
                    ....
                    */
    }

    // 消息发送
    function new_message(e) {
        let $textarea = $('#message-textarea');
        let message_body = $textarea.val().trim();          // 获取输入的新消息, 去除空格
        if (e.which === ENTER_KEY && !e.shiftKey && message_body) {   // 检测到单独按enter键, 没有shift, 消息也不是None
            e.preventDefault();                     // 正常情况enter 是换行, preventDefault是阻止换行
            socket.emit('new message', message_body);  //  home.html 加入了const socket = io('/')用来执行发送事件
            // 第一个参数为事件 new message 名称, message_body 为用户输入的消息正文
            $textarea.val("");                          // 发送完毕清空 消息输入框
        }
    }

    // 有键按下就检验是否为 enter键
    $('#message-textarea').on('keydown', new_message.bind(this));


    // 处理事件函数 , 接收app.py里的new_message发送的emit()里的的 new message事件, 消息显示 到上方聊天框
    // app.py 函数里emit(), 是什么, Js里就接受什么
    socket.on('new message', function (data) {
        $('.messages').append(data.message_html);       // 把新消息append 到总Messages的尾部
        flask_moment_render_all();                      // 将消息中的 时间戳 渲染到网页上
        scrollToBottom();                               //再次计算消息框上到下的距离px, 滚动到最下面
        activateSemantics();                            // 将 ui 组件再激活一次, 似乎不需要这一步
    });

    // 处理事件函数 ,接收app.py里 connect函数发来的emit('user_count', ....., ..)
    socket.on('user_count', function (data) {
        $('#user-count').html(data.count);
        console.log('data.count', data.count)
    });

    // 初始化 导入js后会执行init初始化
    function init() {
        activateSemantics();
        scrollToBottom();

    }

    init();
});
