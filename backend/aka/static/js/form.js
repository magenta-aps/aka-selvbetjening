$(function(){
    console.log("loaded");
    $("form input[required]").attr("data-required", "true").removeAttr("required");
    $("form").submit(function(){
        const $this = $(this);
        var empty = false;
        const requiredMessage = django.format("error.required", null, django.language);
        $this.find("input[data-required]").each(function() {
            if (this.value === '') {
                empty = true;
                const errorContainer = $(".err-msg[for='"+this.id+"']");
                let ul = errorContainer.find("ul.errorlist");
                if (!ul.length) {
                    ul = $("<ul class=\"errorlist\"></ul>");
                    errorContainer.append(ul);
                }
                ul.append("<li data-trans=\"error.required\">"+requiredMessage+"</li>")
            }
        });
        if (empty) {
            return false;
        }
    });
});
