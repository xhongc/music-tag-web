(function($) {

  $.dofresh = function(){
    var refresh_el = $('#refresh_time');
    var time = parseInt(refresh_el.text());
    if(time == 1){
      refresh_el.text(0);
      window.location.reload();
    } else {
      refresh_el.text(time-1);
      setTimeout("$.dofresh()",1000)
    }
  };

  $(function(){
    var refresh_el = $('#refresh_time');
    if(refresh_el){
      setTimeout("$.dofresh()",1000)
    }
  });

})(jQuery);