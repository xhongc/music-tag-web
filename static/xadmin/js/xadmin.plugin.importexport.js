$("#export-menu").click(function () {
    $("input[name='_select_across']").val($("input[name='select_across']").val());
    if (0 == $("input[name='select_across']").val()) {
        var selectedRecords = [];
        $.each($('.action-select'), function () {
            if (true == $(this).prop('checked')) {
                selectedRecords.push($(this).val());
            }
        });
        $("input[name='_selected_actions']").val(selectedRecords.join(','));
    }
});
