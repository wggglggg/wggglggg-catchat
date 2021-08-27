$(document).ready(function () {
    const ENTER_KEY = 13;
    const popupLoading = '<i class="notched circle circle loading icon green"></i>Loading...';
    let message_count = 0;

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
        $('.ui.dropdown').dropdown();

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

        $('#show-snippet-modal').on('click', function () {
            $('.ui.modal.snippet').modal({blurring: true}).modal('show')
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
        message_count++;
        console.log('messcount:', message_count)
        if (!document.hasFocus()) {                 // 如果你在浏览别的窗口, 没有浏览聊天室口, 就在窗口title显示多少条未读
            document.title = '<' + message_count + '>' + 'CatChat';
            console.log('!document.hasFocus', data.user_id !== current_user_id);
        }

        if (data.user_id !== current_user_id) {     // 如果数据拿的用户 不是 当前用户
            console.log(data.user_id !== current_user_id);
            messageNotify(data);
        }

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

    // scroll监听函数
    let page = 1;
    function load_messages() {
        let $messages = $('.messages');
        let position = $messages.scrollTop();       // 判断当前滚动条的位置在哪
        if (position === 0 && socket.nsp !== '/anonymous') {// nsp=namespace 命名空间, 排除掉/anonymaous空间
            page++;
            $('.ui.loader').toggleClass('active');  // 如果侧面滚动条在0位置, 就显示loading
            $.ajax({
                url: messages_url,                  // 打开get_messages网址, 激活get_messages函数
                type: 'GET',
                data: {page: page},
                success: function (data) {
                    let before_height = $messages[0].scrollHeight;  // 0是messages里的一个key, 能获取到窗口当前的高度Px
                    $(data).prependTo('.messages').hide().fadeIn(2000);  //插入消息, 插入时会隐藏, 再淡显示延时1000
                    let after_height = $messages[0].scrollHeight;   // 加入消息后, 再获取高度
                    flask_moment_render_all();                      // 后加的消息后面跟时间戳, 不然新刷新的消息没时间
                    $messages.scrollTop(after_height - before_height); // 加入后的高度 - 加入前的高度, 新刷新消息的高度
                    $('.ui.loader').toggleClass('active');
                    activateSemantics();
                },
                error: function () {
                    alert('No more messages.');                     // 如果消息已经全部更新出来, 就显示"没有多余的消息了"
                    $('.ui.loader').toggleClass('active');
                }
            });
        }
    }
    $('.messages').scroll(load_messages);

    $('#show-help-modal').on('click', function () {
        $('.ui.modal.help').modal({blurring:true}).modal('show')        //blurring:true  就是开启模糊modal
    });

    // 发送消息提醒
    function messageNotify(data) {          // 如果没权限 , 就申请 权限 , 如果有权限就发送消息, 去掉特殊符号
        if (Notification.permission !== 'granted')
            Notification.requestPermission();
        else {
            var notification = new Notification('Message from' + data.nickname, {
               icon: data.gravatar,         //  要发送的消息
               body: data.message_body.replace(/(<([^>]+)>)/ig, ""), // 将标点括号都去掉
            });

            notification.onclick = function () {            // 提醒消息被 单击为打开主页
                window.open(root_url);
            };
            setTimeout(function () {
                notification.close()
            }, 4000)
        }
    }

    // 初始化 导入js后会执行init初始化
    function init() {
        $(window).focus(function () {           // 当你再次浏览catchat窗口时, 把消息提醒给清0
            message_count = 0;
            document.title = 'wggglggg-catchat'
        });

        document.addEventListener('DOMContentLoaded', function () {
            if (!Notification) {                    //  创建一个监听器, 浏览器打开后, 如果notification不支持, 就提示
                alert('Desktop notifications not available in your browser');
                console.log('!Notification');
                return;
            }

            if (Notification.permission !== 'granted')        // 如果发现浏览器权限是不允许 , 就申请 权限
                Notification.requestPermission();

        });
        console.log('notify');

        // 短消息发送
        $('#snippet-button').on('click', function () {
            let $snippet_textarea = $('#snippet-textarea');
            let message = $snippet_textarea.val();
            if (message.trim() !=='') {
                socket.emit('new message', message);
                $snippet_textarea.val('');
            }
        });

        // 回复消息
        $('.quote-button').on('click', function () {
           let $textarea = $('#message-textarea');
           let message = $(this).parent().parent().parent().find('.message-body').text(); // 被回复的消息
            $textarea.val('>' + message + '\n\n');
            $textarea.val($textarea.val()).focus();
        });

        activateSemantics();
        scrollToBottom();
    }

    $('.delete-button').on('click', function () {
        let $this = $(this);
        $.ajax({
            type: 'DELETE',
            url: $this.data('href'),
            success: function () {
                $this.parent().parent().parent().remove();
            },
            error: function () {
                alert('Oops, something was wrong')
            }
        });
    });

    $(document).on('click', '.delete-user-btn', function () {
        let $this = $(this);
        $.ajax({
            type: 'DELETE',
            url: $this.data('href'),
            success: function () {
                $this.parent().parent().parent().parent().remove();
                alert('Success, this user is gone!')
            },
            error: function () {
                alert('Oops, something was wrong')
            }
        });
    });

    init();
});
