

$(function(){

    const tables = $(".output-table");
    const datatables = {};

    const columnIndexes = {};
    tables.each(function () {
        const thistable = $(this),
            key = thistable.attr("data-key");
        datatables[key] = thistable.DataTable({
            scrollX: true,
            searching: false,
            lengthChange: false,
            paging: false,
            info: false,
            fixedHeader: true,
        });
        columnIndexes[key] = {};
        $(".dataTables_scrollHeadInner .output-table[data-key='"+key+"'] th").each(function (index, el) {
            columnIndexes[key][$(el).data("field")] = index;
        });
    });

    var columnSelect = $(".columnselect");
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

    const updateColumns = function() {
        const $this = $(this),
            key = $this.attr("data-key"),
            showColumns = $this.val(),
            hash = {};

        console.log("showColumns",showColumns);
        for (var i=0; i<showColumns.length; i++) {
            hash[showColumns[i]] = true;
        }
        for (let field in columnIndexes[key]) {
            const show = hash[field] || false;
            const index = columnIndexes[key][field];
            datatables[key].column(index).visible(show);
            field = key + "." + field;
            if (show) {
                $("input[name='hidden'][value='"+field+"']").remove();
            } else if (!($("input[name='hidden'][value='"+field+"']").length)) {
                $("form").append('<input type="hidden" name="hidden" value="' + field + '"/>');
            }
        }
    };

    columnSelect.change(updateColumns);
    columnSelect.each(updateColumns);

    //columnSelect.find("option").prop("selected", true);
    $("input[name=hidden]").each(function () {
        const value = $(this).val().split('.'),
            key = value[0],
            field = value[1],
            headers = $(".output-table[data-key='"+key+"']").find("th"),
            header = headers.filter("th[data-field='"+field+"']").first(),
            //index = headers.index(header),
            index = columnIndexes[key][field],
            column = datatables[key].column(index);
        column.visible(false);
        //columnSelect.filter("[data-key='"+key+"']").find("option[value='"+field+"']").prop("selected", false);
    });

    $(document).on('language-change', function(event, language) {
        for (let key in datatables) {
            if (datatables.hasOwnProperty(key)) {
                datatables[key].draw();
            }
        }
        columnSelectMessage = django.gettext(language, "common.showcolumns");
        for (var i=0; i<sumo.length; i++) {
            sumo[i].setText();
        }
    });

    $(".collapsed[data-key]").on("expanded", function() {
        const key = $(this).data("key");
        if (key && datatables[key]) {
            datatables[key].draw();
        }
    });
});

