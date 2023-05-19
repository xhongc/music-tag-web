;(function($) {
    $.fn.formset = function(opts){
        var $$ = $(this);

        var options = $.extend({
            prefix: $$.data('prefix')
        }, $.fn.formset.styles[$$.data('style')], opts),

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
                if (elem.attr('href')) elem.attr('href', elem.attr('href').replace(idRegex, replacement));
                elem.find('.formset-num').html(ndx + 1);
            },

            hasChildElements = function(row) {
                return row.find('input,select,textarea,label,div,a').length > 0;
            },

            updateRowIndex = function(row, i){
                if (options.update) options.update(row, (function(elem){
                    updateElementIndex(elem, options.prefix, i);
                }));
                updateElementIndex(row, options.prefix, i);
                row.find('input,select,textarea,label,div,a').each(function() {
                    updateElementIndex($(this), options.prefix, i);
                });
                row.data('row-index', i);
            },

            insertDeleteLink = function(row) {
                row.find('a.delete-row').click(function() {
                    var row = $(this).parents(".formset-row"),
                        del = row.find('input[id $= "-DELETE"]');

                    if (options.removed) options.removed(row, del, $$);

                    if (del.length) {
                        if(del.val() == 'on'){
                            row.removeClass('row-deleted');
                        } else {
                            row.addClass('row-deleted');
                        }
                        del.val(del.val() == 'on'?'':'on');
                    } else {
                        var parent = row.parent();
                        row.remove();
                        var forms = parent.find('.formset-row');
                        $('#id_' + options.prefix + '-TOTAL_FORMS').val(forms.length);
                        for (var i=0, formCount=forms.length; i<formCount; i++) {
                            updateRowIndex(forms.eq(i), i);
                        }
                    }
                    return false;
                });
            };

        $$.find(".formset-row").each(function(i) {
            insertDeleteLink($(this));
        });

        if ($$.length) {
            var template, el = $('#' + options.prefix + '-empty');
            if(el.is('textarea')) {
                template = el.val();
            } else if(el.is('span')) {
                template = el.html();
            }else if(el.is('script')) {
                template = el.html();
            }

            template = el.html(template).text(); // decoded
            template = $($.parseHTML(template));

            template.removeAttr('id');
            if(template.data("replace-id")){
                template.attr('id', template.data("replace-id"));
                template.removeAttr('data-replace-id');
            }
            options.formTemplate = template;

            $('#' + options.prefix + '-add-row').click(function() {
                var formCount = parseInt($('#id_' + options.prefix + '-TOTAL_FORMS').val()),
                    row = options.formTemplate.clone(true).removeClass('empty-form');
                updateRowIndex(row, formCount);
                row.appendTo($$);
                insertDeleteLink(row);
                row.exform();
                $('#id_' + options.prefix + '-TOTAL_FORMS').val(formCount + 1);
                // If a post-add callback was supplied, call it with the added form:
                if (options.added) options.added(row, $$);
                return false;
            });
        }

        return $$;
    }

    $.fn.formset.styles = {
        'tab': {
            added: function(row, $$){
                var new_tab = $('<li><a data-toggle="tab" href="#'+ row.attr('id') +'">#<span class="formset-num">'+ (row.data('row-index') + 1) +'</span></a></li>');
                $$.parent().find('.nav-tabs').append(new_tab);
                new_tab.find('a').tab('show');
            },
            update: function(row, update){
                var rowId = row.attr('id');
                if(rowId){
                    $('a[href=#'+rowId+']').each(function(){
                        update($(this));
                    })
                }
            },
            removed: function(row, del, $$){
                var rowId = row.attr('id');
                if(rowId){
                    var tab = $('a[href=#'+rowId+']');
                    if (del.length) {
                        if(del.val() == 'on'){
                            tab.removeClass('row-deleted');
                        } else {
                            tab.addClass('row-deleted');
                        }
                    } else {
                        if(tab.parent().next().length){
                            tab.parent().next().find('a').tab('show');
                        } else {
                            tab.parent().prev().find('a').tab('show');
                        }
                        tab.parent().remove();
                    }
                }
            }
        }
    };

    $(function(){
        $('.formset-content').each(function(){
            $(this).formset();
        });
    });
})(jQuery);
