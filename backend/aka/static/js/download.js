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
        form.append('<input type="hidden" name="key" value="'+key+'"/>');
        form.append('<input type="hidden" name="format" value="'+format+'"/>');
        form.submit();
    });
});
