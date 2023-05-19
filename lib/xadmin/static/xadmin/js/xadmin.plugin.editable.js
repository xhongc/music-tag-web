
+function ($) { "use strict";

  // POPOVER PUBLIC CLASS DEFINITION
  // ===============================

  var Editpop = function (element, options) {
    this.einit('editpop', element, options)
  }

  Editpop.DEFAULTS = $.extend({} , $.fn.popover.Constructor.DEFAULTS, {
    container: 'body'
  , trigger: 'manual'
  , placement: function(tip, el) {
    var $tip = $(tip)
    var $el = $(el)

    var tip_width = $tip.width(),
        tip_height = $tip.height(),
        el_width = $el.width(),
        el_height = $el.height(),
        client_width = document.body.clientWidth,
        gap = 20

    var top_gap = $el.offset().top - $("body").scrollTop() - 40,
        left_gap = $el.offset().left - $("body").scrollLeft(),
        right_gap = client_width - left_gap - el_width

    if(top_gap > tip_height + gap && left_gap > tip_width/2 + gap && right_gap > tip_width/2 + gap){
      return 'top'
    }
    if(top_gap > tip_height/2){
      if(right_gap > tip_width + gap){
        return 'right'
      } else if(left_gap > tip_width + gap) {
        return 'left'
      }
    }
    return 'bottom'
  }
  , template: '<div class="popover editpop editable"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
  })


  // NOTE: POPOVER EXTENDS tooltip.js
  // ================================

  Editpop.prototype = $.extend({}, $.fn.popover.Constructor.prototype)

  Editpop.prototype.constructor = Editpop

  Editpop.prototype.einit = function (type, element, options) {
    this.init(type, element, options)
    this.content = null
    this.$element.on('click.' + this.type, $.proxy(this.beforeToggle, this))

    this.$text = this.$element.parent().parent().find('.editable-field')
    this.field = this.$element.data('editable-field')
  }

  Editpop.prototype.getDefaults = function () {
    return Editpop.DEFAULTS
  }

  Editpop.prototype.beforeToggle = function() {
    var $el = this.$element

    if(this.content == null){
      var that = this
      $el.find('>i').removeClass('fa fa-edit').addClass('fa fa-spinner fa-spin')
      $.ajax({
        url: $el.data('editable-loadurl'),
        success: function(content){
          $el.find('>i').removeClass('fa fa-spinner fa-spin').addClass('fa fa-edit')
          that.content = content
          that.toggle()
        },
        dataType: 'html'
      })
    } else {
      this.toggle()
    }
  }

  Editpop.prototype.setContent = function () {
    var $tip    = this.tip()
    var title   = this.getTitle()

    $tip.find('.popover-title').html('<button class="close" data-dismiss="editpop">&times;</button>' + title)
    $tip.find('.popover-content').html(this.content)

    var $form = $tip.find('.popover-content > form')
    $form.exform()
    $form.submit($.proxy(this.submit, this))

    this.$form = $form
    this.$mask = $('<div class="mask"><h2 style="text-align:center;"><i class="fa-spinner fa-spin fa fa-large"></i></h2></div>')
    $tip.find('.popover-content').prepend(this.$mask)

    $tip.removeClass('fade top bottom left right in')

    //bind events
    $tip.find('[data-dismiss=editpop]').on('click.' + this.type, $.proxy(this.leave, this, this))

    var me = ((Math.random() * 10) + "").replace(/\D/g, '')
    var click_event_ns = "click." + me + " touchstart." + me
    var that = this

    // $('body').on(click_event_ns, function(e) {
    //   if ( !$tip.has(e.target).length ) { that.hide() }
    // })

    $(document).bind('keyup.editpop', function(e) {
      if (e.keyCode == 27) { that.leave(that) }
      return
    })
  }

  Editpop.prototype.hasContent = function () {
    return this.getTitle() || this.content
  }

  Editpop.prototype.submit = function(e) {
      e.stopPropagation()
      e.preventDefault()
      
      $.when(this.save())
      .done($.proxy(function(data) {
        this.$mask.hide()
        this.$mask.parents('.popover').hide()
        if(data['result'] != 'success' && data['errors']){
          var err_html = []
          for (var i = data['errors'].length - 1; i >= 0; i--) {
            var e = data['errors'][i]
            for (var j = e['errors'].length - 1; j >= 0; j--) {
              err_html.push('<span class="help-block error">'+e['errors'][j]+'</span>')
            }
          }
          this.$form.find(".control-group").addClass('has-error')
          this.$form.find('.controls').append(err_html.join('\n'))
        } else {
          this.$text.html(data['new_html'][this.field])
          this.leave(this)
        }
      }, this))
      .fail($.proxy(function(xhr) {
        this.$mask.hide()
        this.$mask.parents('.popover').hide()
        alert(typeof xhr === 'string' ? xhr : xhr.responseText || xhr.statusText || 'Unknown error!');
      }, this))
  }

  Editpop.prototype.save = function(newValue) {
    this.$form.find('.control-group').removeClass('has-error')
    this.$form.find('.controls .help-block.error').remove()

    this.$mask.show()

    var off_check_box = Object();
    this.$form.find('input[type=checkbox]').each(function(){
      if(!$(this).is(':checked')){
        off_check_box[$(this).attr('name')] = ''
      }
    })

    return $.ajax({
      data: [this.$form.serialize(), $.param(off_check_box)].join('&'),
      url: this.$form.attr('action'),
      type: "POST",
      dataType: 'json',
      beforeSend: function(xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", $.getCookie('csrftoken'))
      }
    })
  }

  // POPOVER PLUGIN DEFINITION
  // =========================

  var old = $.fn.editpop

  $.fn.editpop = function (option) {
    return this.each(function () {
      var $this   = $(this)
      var data    = $this.data('bs.editpop')
      var options = typeof option == 'object' && options

      if (!data) $this.data('bs.editpop', (data = new Editpop(this, options)))
      if (typeof option == 'string') data[option]()
    })
  }

  $.fn.editpop.Constructor = Editpop


  // POPOVER NO CONFLICT
  // ===================

  $.fn.editpop.noConflict = function () {
    $.fn.editpop = old
    return this
  }

  $(function(){
    $('.editable-handler').editpop();
  })

}(window.jQuery);
