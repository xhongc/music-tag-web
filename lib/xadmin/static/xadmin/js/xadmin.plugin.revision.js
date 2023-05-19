jQuery(function($){
    $('.diff_field').each(function(){
        var el = $(this);
        var textarea = el.find('textarea.org-data');
        var title = el.data('org-data') || el.attr('title');
        if(textarea.length){
            title = textarea.val();
        }
        el.find('.controls').tooltip({
            title: title,
            html: true
        })
    });

    $('.formset-content .formset-row').each(function(){
        var row = $(this);
        var del = row.find('input[id $= "-DELETE"]');
        if(del.val() == 'on' || del.val() == 'True'){
            row.addClass('row-deleted');
            del.val('on');
        }
        var idinput = row.find('input[id $= "-id"]');
        if(idinput.val() == '' || idinput.val() == undefined){
            row.addClass('row-added');
            row.find('.formset-num').html(gettext('New Item'));
        }
    });
});