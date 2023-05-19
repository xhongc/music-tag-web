(function($) {
    $(function() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie != '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = jQuery.trim(cookies[i]);
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        });

        $(".results table tbody").sortable({
            axis: 'y',
            items: 'tr',
            cursor: 'move',
            opacity: 0.8,
            update: function(event, ui) {
                var $rows = $(this);
                $("#save-order").on("click", function(e) {
                    $.ajax({
                        url: $(this).attr('post-url'),
                        method: 'POST',
                        data: $rows.sortable('serialize', {
                            attribute: 'order-key',
                            expression: (/(.+)_(.+)/),
                        })
                    });
                    location.reload();
                }).show();
            }
        });
    });

})(jQuery);
