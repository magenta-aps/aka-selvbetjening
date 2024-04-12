$(function(){
    var downloadSelect = $("select#download");
    var selectMessage = django.gettext(django.language, "common.download");
    downloadSelect.SumoSelect();
    downloadSelect.each(function() {
        this.sumo.setText = function(){
            this.caption.html(selectMessage);
        };
        this.sumo.setText();
    });
    downloadSelect.change(function() {
        const form = downloadSelect.parents("form");
        const s = this.value.split("."),
            key = s[0],
            format = s[1];
        const keyField = $('<input type="hidden" name="key" value="'+key+'"/>');
        const formatField = $('<input type="hidden" name="format" value="'+format+'"/>');
        form.append(keyField, formatField);
        form.attr("target", "_blank");
        form.submit();
        keyField.remove();
        formatField.remove();
        form.removeAttr("target");
    });
});
