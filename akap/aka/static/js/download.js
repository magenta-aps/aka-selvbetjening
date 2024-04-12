$(function(){
$(".download a").on("click", function() {
        const form = $("form");
        const s = $(this).data("format").split("."),
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
