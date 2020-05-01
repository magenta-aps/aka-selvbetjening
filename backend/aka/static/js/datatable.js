$(function(){
    var table = $('#data-table').DataTable({
        scrollX: true
    });

    $("[data-action='display-column']").each(function(index, element){
        $(element).attr("data-column-index", index);
    });

    var columnSelect = $("[name=columns]");
    columnSelect.SumoSelect();
    columnSelect.each(function() {
        this.sumo.setText = function(){
            this.caption.html("Vis/skjul kolonner");
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
});
