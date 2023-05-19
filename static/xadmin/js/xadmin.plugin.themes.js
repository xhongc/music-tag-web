(function($) {

  $.setCookie = function(name, value, options){
    options = options || {};
    if (value === null) {
        value = '';
        options.expires = -1;
    }
    var expires = '';
    if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
        var date;
        if (typeof options.expires == 'number') {
            date = new Date();
            date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
        } else {
            date = options.expires;
        }
        expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
    }
    var path = options.path ? '; path=' + options.path : '';
    var domain = options.domain ? '; domain=' + options.domain : '';
    var secure = options.secure ? '; secure' : '';
    document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
  }

  $(function(){
    var top_nav = $('#top-nav');
    $('#body-content').css('margin-top', (top_nav.height() + 15) + 'px');

    if($("#g-theme-menu")){
      $('#g-theme-menu li>a').click(function(){
        var $el = $(this);
        var themeHref = $el.data('css-href');
        
        var topmenu = $('#top-nav .navbar-collapse');
        if(topmenu.data('bs.collapse')) topmenu.collapse('hide');

        var modal = $('<div id="load-theme-modal" class="modal fade" role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
            'Loading theme</h4></div><div class="modal-body"><h2 style="text-align:center;"><i class="fa-spinner fa-spin fa fa-large"></i></h2></div></div></div></div>');
        $('body').append(modal);

        modal.on('shown.bs.modal', function(){
          $.save_user_settings("site-theme", themeHref, function(){
            $.setCookie('_theme', themeHref);

            var iframe = document.createElement("IFRAME");
            iframe.style.display = 'none';
            document.body.appendChild(iframe);

            modal.on('hidden', function(e){
              if(iframe){
                $(iframe).unbind('load');
                iframe.parentNode.removeChild(iframe);
                iframe = null;
              }
              modal.remove();
            });

            $(iframe).load(function () {
              $('#site-theme').attr('href', themeHref);

              setTimeout(function(){
                var nav_height = $('#top-nav').height();
                $('#body-content').animate({'margin-top': (nav_height + 15)}, 500, 'easeOutBounce');
              }, 500);

              modal.modal('hide');
              iframe.parentNode.removeChild(iframe);
              iframe = null;
            })

            var ifmDoc = iframe.contentDocument || iframe.contentWindow.document;
            ifmDoc.open();
            ifmDoc.write('<!doctype><html><head></head><body>');
            ifmDoc.write('<link rel="stylesheet" href="'+themeHref+'" />');
            ifmDoc.write('</body></html>');
            ifmDoc.close();


            $('#g-theme-menu li').removeClass('active');
            $el.parent().addClass('active');
          });
        })

        modal.modal().css(
            {
                'margin-top': function () {
                    return window.pageYOffset;
                }
            });
      })
    }
  });

})(jQuery);