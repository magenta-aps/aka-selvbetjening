$(function(){
    $("form input[required]").attr("data-required", "true").removeAttr("required");
    $("form").submit(function(){
        const $this = $(this);
        var error = false;
        $("ul.errorlist")
        const requiredMessage = django.format("error.required", null, django.language);
        $this.find("input[data-required]").each(function() {
            if (this.value === '') {
                error = true;
                const errorContainer = $(".err-msg[for='"+this.id+"']");
                let ul = errorContainer.find("ul.errorlist");
                if (!ul.length) {
                    ul = $("<ul class=\"errorlist\"></ul>");
                    errorContainer.append(ul);
                }
                ul.append("<li data-trans=\"error.required\">"+requiredMessage+"</li>")
            }
        });

        const invalidDateAfterMessage = django.format("error.from_date_before_to_date", null, django.language);
        $this.find("input[data-validate-after]").each(function() {
            var comparisonField = $($(this).attr("data-validate-after"));
            if (this.value && comparisonField.val() && strpdate(this.value) < strpdate(comparisonField.val())) {
                error = true;
                const errorContainer = $(".err-msg[for='"+this.id+"']");
                let ul = errorContainer.find("ul.errorlist");
                if (!ul.length) {
                    ul = $("<ul class=\"errorlist\"></ul>");
                    errorContainer.append(ul);
                }
                ul.append("<li data-trans=\"error.from_date_before_to_date\">"+invalidDateAfterMessage+"</li>")
            }
        });

        if (error) {
            return false;
        }
    });

    var strpdate = function(dateString) {
        var match = /(\d{2})\/(\d{2})\/(\d{4})/.exec(dateString);
        if (match) {
            return new Date(match[3], match[2], match[1]);
        }
        return null;
    };
});
