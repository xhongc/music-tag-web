
;(function($){

  $.fn.exform.renders.push(function(f){
    if($.fn.multiselect){
      f.find('.selectmultiple.selectdropdown').multiselect({
        
      });
    }
  });

})(jQuery)