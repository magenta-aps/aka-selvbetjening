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

    $("form input, form select").on("keyup change", function(){
        validate.call(this);
    });

    const numberRegex = /^\d+([,\.]\d+)?$/;
    const cprRegex = /^\d{10}$/;
    const validate = function() {
        $(".err-msg[for='"+this.id+"'] ul.errorlist").empty();
        $("div.has-error[data-field='"+this.id+"']").removeClass("has-error");
        const $this = $(this);
        let error = false;
        if ($this.attr("data-required")) {
            if (this.value === '') {
                error = true;
                addError(this.id, "error.required");
            }
        }

        if ($this.attr("data-number")) {
            if (this.value && !numberRegex.exec(this.value)) {
                error = true;
                addError(this.id, "error.number_required");
            }
        }

        if ($this.attr("data-cpr")) {
            if (this.value && !cprRegex.exec(this.value)) {
                error = true;
                addError(this.id, "error.invalid_cpr");
            }
        }

        if ($this.attr("data-validate-after")) {
            var comparisonField = $($(this).attr("data-validate-after"));
            if (this.value && comparisonField.val() && strpdate(this.value) < strpdate(comparisonField.val())) {
                error = true;
                addError(this.id, $(this).attr("data-validate-after-errormessage"));
            }
        }
        const reverseDateComparator = $("[data-validate-after='#"+this.id+"']");
        if (reverseDateComparator.length) {
            validate.call(reverseDateComparator.get(0));
        }

        return error;
    };

    $("form").submit(function(){
        var error = false;
        $("form input, form select").each(function(){
            if (validate.call(this)) {
                error = true;
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
