$(function(){
    $("form input[required]").attr("data-required", "true").removeAttr("required");
    $("form input[type=number]").attr({"data-number": "true", "type": "text"});

    const addError = function(id, errorkey) {
        const errorContainer = $(".err-msg[for='"+id+"']");
        let ul = errorContainer.find("ul.errorlist");
        if (!ul.length) {
            ul = $("<ul class=\"errorlist\"></ul>");
            errorContainer.append(ul);
        }
        ul.append("<li data-trans=\""+errorkey+"\">"+django.format(errorkey, null, django.language)+"</li>");
    };

    const clearError = function() {
        console.log("clearError",this,this.id);
        $(".err-msg[for='"+this.id+"'] ul.errorlist").empty();
        $("div.has-error[data-field='"+this.id+"']").removeClass("has-error");
    };

    $("form input, form select").on("keyup change", clearError);

    $("form").submit(function(){
        const $this = $(this);
        $("form input, form select").each(clearError);
        var error = false;
        $this.find("input[data-required]").each(function() {
            if (this.value === '') {
                error = true;
                addError(this.id, "error.required");
            }
        });

        const numberRegex = /^\d+([,\.]\d+)?$/;
        $this.find("input[data-number]").each(function() {
            if (this.value && !numberRegex.exec(this.value)) {
                error = true;
                addError(this.id, "error.number_required");
            }
        });

        const cprRegex = /^\d{10}$/;
        $this.find("input[data-cpr]").each(function() {
            if (this.value && !cprRegex.exec(this.value)) {
                error = true;
                addError(this.id, "error.invalid_cpr");
            }
        });

        $this.find("input[data-validate-after]").each(function() {
            var comparisonField = $($(this).attr("data-validate-after"));
            if (this.value && comparisonField.val() && strpdate(this.value) < strpdate(comparisonField.val())) {
                error = true;
                addError(this.id, "error.from_date_before_to_date");
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
