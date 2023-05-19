(function($){

  var DetailsPop = function(element){
    this.$element = $(element);
    this.res_uri = this.$element.data('res-uri');
    this.edit_uri = this.$element.data('edit-uri');
    this.obj_data = null;

    this.$element.on('click', $.proxy(this.click, this));
  };

  DetailsPop.prototype = {
      constructor: DetailsPop,

      click: function(e){
        e.stopPropagation();
        e.preventDefault();
        var modal = $('#detail-modal-id');
        var el = this.$element;
        if(!modal.length){
          modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
            '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4 class="modal-title">'+ 
            el.attr('title') +'</h4></div><div class="modal-body"></div>'+
            '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">'+gettext('Close')+'</button>'+
            '<a class="btn btn-submit btn-primary edit-btn"><i class="fa fa-pencil"></i> '+gettext('Edit')+'</a></div></div></div></div>');
          $('body').append(modal);
        }
        modal.find('.modal-title').html(el.attr('title'));
        var edit_btn = modal.find('.edit-btn');
        if(this.edit_uri != ""){
          edit_btn.attr('href', this.edit_uri);
        }else{
          edit_btn.remove();
        }
        modal.find('.modal-body').html('<h1 style="text-align:center;"><i class="fa-spinner fa-spin fa fa-large"></i></h1>');
        modal.find('.modal-body').load(this.res_uri + '?_format=html', function(response, status, xhr) {
          if (status == "error") {
            var msg = "Sorry but there was an error: ";
            modal.find('.modal-body').html(msg + xhr.status + " " + (typeof xhr === 'string' ? xhr : xhr.responseText || xhr.statusText || 'Unknown error!'));
          }
        });
        modal.modal();
      }
  };

  $.fn.details = function () {
    return this.each(function () {
      var $this = $(this), data = $this.data('details');
      if (!data) {
          $this.data('details', (data = new DetailsPop(this)));
      }
    });
  };

  $(function(){
    $('.details-handler').details();
  });

})(jQuery);


