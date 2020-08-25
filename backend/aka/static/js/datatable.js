$(function(){
    var table = $('.output-table').DataTable({
        scrollX: true,
        searching: false,
        lengthChange: false,
        paging: false,
        info: false,
        fixedHeader: true,
        buttons: [
            'pdf'
        ]
    });

    $("[data-action='display-column']").each(function(index, element){
        $(element).attr("data-column-index", index);
    });

    var columnSelect = $("[name=columns]");
    var columnSelectMessage = django.gettext(django.language, "common.showcolumns");
    var sumo = [];
    columnSelect.SumoSelect();
    columnSelect.each(function() {
        sumo.push(this.sumo);
        this.sumo.setText = function(){
            this.caption.html(columnSelectMessage);
        };
        this.sumo.setText();
    });

    var headers = $('#data-table th');

    columnSelect.change(function() {
        var showColumns = $(this).val();
        var hash = {};

        for (var i=0; i<showColumns.length; i++) {
            hash[showColumns[i]] = true;
        }

        headers.each(function(index, el) {
            var field = $(this).attr("data-field");
            var show = hash[field] || false;
            table.column(index).visible(show);
            if (show) {
                $("input[name=hidden][value="+field+"]").remove();
            } else if (!($("input[name=hidden][value="+field+"]").length)) {
                $("form").append('<input type="hidden" name="hidden" value="' + field + '"/>');
            }
        });
    });

    $("input[name=hidden]").each(function () {
        var field = $(this).val();
        var header = $('#data-table th[data-field='+field+']').first();
        var headers = $('#data-table th');
        var index = headers.index(header);
        var column = table.column(index);
        column.visible(false);
    });

    $(document).on('language-change', function(event, language) {
        table.draw();
        columnSelectMessage = django.gettext(language, "common.showcolumns");
        for (var i=0; i<sumo.length; i++) {
            sumo[i].setText();
        }
    });
});
