jQuery(function() {
  $( ".btn-quick-form" ).click(function(){
    var btn = $(this),
        form_url;
    if(btn.is('a')){
      form_url = btn.attr('href');
    }
    if(form_url == undefined){
      form_url = btn.data('form-url');
    }
    if(!btn.data('form-modal')){
      var modal = $('<div class="modal hide fade quick-form" role="dialog"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3>'+ 
        btn.attr('title') +'</h3></div><div class="modal-body"></div>'+
        '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">'+gettext('Close')+'</button>'+
        '<a class="btn btn-primary btn-submit">'+gettext('Save changes')+'</a></div></div>');
      $('body').append(modal);
      btn.data('form-modal', modal);
      modal.find('.modal-body').load(form_url, function(form_html, status, xhr){
        var form = $(this).find('form');
        form.exform();
        modal.find('.btn-submit').click(function(){
          var csrftoken = $.getCookie('csrftoken');
          //clean form errors
          form.find('.text-error,.help-inline.error').remove();
          form.find('.control-group').removeClass('error');          
          $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function(data){
              if(data['result'] != 'success' && data['errors']){
                var non_fields_errors = [];
                for (var i = data['errors'].length - 1; i >= 0; i--) {
                  var e = data['errors'][i];
                  var errdiv = form.find('#div_' + e['id']);
                  if(errdiv.length){
                    errdiv.addClass('error');
                    var err_html = [];
                    for (var i = e['errors'].length - 1; i >= 0; i--) {
                      err_html.push('<span id="error_'+i+'_'+ e['id'] +'" class="help-inline error"><strong>'+e['errors'][i]+'</strong></span>');
                    };
                    errdiv.find('.controls').append(err_html.join('\n'));
                  } else {
                    non_fields_errors = non_fields_errors.concat(e['errors']);
                  }
                };
                if(non_fields_errors.length){
                  var err_html = [];
                  for (var i = non_fields_errors.length - 1; i >= 0; i--) {
                    err_html.push('<p class="text-error"><strong>'+e['errors'][i]+'</strong></p>');
                  };
                  form.prepend(err_html.join('\n'));
                }
              } else {
                btn.trigger('post-success');
              }
            },
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
          });
        })
      });
    }
    btn.data('form-modal').modal().css(
        {
            'margin-top': function () {
                return window.pageYOffset;
            }
        });
    return false;
  });

  $('.btn-quick-form').on('post-success', function(e){
    window.location.reload();
  });
});