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
        window.location = this.value;
    });

});
