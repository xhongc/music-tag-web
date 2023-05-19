
;(function($){

  $('.batch-field-checkbox').bind('click', function(event){
      if (!event) { var event = window.event; }
      var target = event.target ? event.target : event.srcElement;

      var wrap = $(this).parent().parent().find('.control-wrap');
      if(target.checked){
        wrap.show('fast');
      } else {
        wrap.hide('fast');
      }
  });

})(jQuery)
