jQuery(function() {
    $( ".column" ).sortable({
        connectWith: ".column",
        handle: '.panel-heading',
        forcePlaceholderSize: true,
        cursor: "move",
        cancel: ".unsort, .tab-content",
        stop: function( event, ui ) {
            var pos = [];
            $('.column').each(function(){
                var col = [];
                $(this).find('.panel').each(function(){
                    col.push($(this).attr('id'));
                });
                pos.push(col.join(','));
            });
            var pos_val = pos.join('|');
            var key = $('#_portal_key').val();
            $.save_user_settings(key, pos_val, function(){
                //alert('success');
            });
        }
    });

    $( ".panel-heading .icon.chevron" ).click(function() {
        $( this ).toggleClass( "fa fa-chevron-up" ).toggleClass( "fa fa-chevron-down" );
        $( this ).parents( ".panel:first" ).find( ".panel-body" ).toggle('fast');
    });
    
});