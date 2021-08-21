$(document).ready(function () {
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
        const popupLoading = '<i class="notched circle circle loading icon green"></i>Loading...'

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

    // 初始化 导入js后会执行init初始化
    function init() {
        activateSemantics();
        scrollToBottom();

    }

    init();
});
