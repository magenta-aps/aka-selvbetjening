// https://stackoverflow.com/questions/2360655/jquery-event-handlers-always-execute-in-order-they-were-bound-any-way-around-t
$.fn.bindFirst = function(name, fn) {
    this.on(name, fn);
    this.each(function() {
        const eventtypes = name.split(" ");
        for (let i=0; i<eventtypes.length; i++) {
            const handlers = $._data(this, 'events')[eventtypes[i].split('.')[0]];
            const handler = handlers.pop();
            handlers.splice(0, 0, handler);
        }
    });
};

$(function(){
    $("input[required]").attr("data-required", "true").removeAttr("required");
    $("input[type=number]").attr({"data-number": "true", "type": "text"});

    const addError = function(id, errorkey) {
        const errorContainer = $(".err-msg[for='"+id+"']");
        let ul = errorContainer.find("ul.errorlist");
        if (!ul.length) {
            ul = $("<ul class=\"errorlist\"></ul>");
            errorContainer.append(ul);
        }
        ul.append("<li data-trans=\""+errorkey+"\">"+django.format(errorkey, null, django.language)+"</li>");
    };


    const numberRegex = /^(((\d{1,3})(\.\d{3})*)|\d+)([,]\d+)?$/;
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

    $("form input, form select").on("keyup change", function(){
        validate.call(this);
    });

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

    $("[data-collapse]").click(function () {
        const target = $($(this).attr("data-collapse"));
        target.toggleClass("collapsed");
        if (target.hasClass("collapsed")) {
            $(this).addClass("has-collapsed");
            $(this).removeClass("has-expanded");
            target.slideUp({complete: function () {
                target.trigger("collapsed");
            }});
        } else {
            $(this).removeClass("has-collapsed");
            $(this).addClass("has-expanded");
            target.slideDown({complete: function () {
                target.trigger("expanded");
            }});
        }
    })
});
