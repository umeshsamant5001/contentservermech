function changer() {
    $('select[name=program_list]').change(function() {
        var program_id = $(this).val();
        console.log(program_id);
    });
}
