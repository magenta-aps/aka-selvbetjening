$(function() {
    const globals = window;
    const django = globals.django || (globals.django = {});
    if (!django.catalog) django.catalog = {};

    if (!django.jsi18n_initialized) {
        django.gettext = function(language, msgid) {
            var value = django.catalog[language][msgid];
            if (typeof(value) == 'undefined') {
                return msgid;
            } else {
                return (typeof(value) == 'string') ? value : value[0];
            }
        };

        django.ngettext = function(language, singular, plural, count) {
            var value = django.catalog[language][singular];
            if (typeof(value) == 'undefined') {
                return (count === 1) ? singular : plural;
            } else {
                return value.constructor === Array ? value[django.pluralidx(count)] : value;
            }
        };

        django.gettext_noop = function(msgid) { return msgid; };

        django.pgettext = function(language, context, msgid) {
            var value = django.gettext(language, context + '\x04' + msgid);
            if (value.indexOf('\x04') !== -1) {
                value = msgid;
            }
            return value;
        };

        django.npgettext = function(language, context, singular, plural, count) {
            var value = django.ngettext(language, context + '\x04' + singular, context + '\x04' + plural, count);
            if (value.indexOf('\x04') !== -1) {
                value = django.ngettext(language, singular, plural, count);
            }
            return value;
        };

        django.interpolate = function(fmt, obj, named) {
            if (named) {
                return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
            } else {
                return fmt.replace(/%s/g, function(match){return String(obj.shift())});
            }
        };

        $("*[data-locale-changer]").each(function(){
            const langChooser = $(this);
            const flagElements = $(langChooser.attr("data-locale-flag"));
            const update = function(){
                const language = $(this).val();
                flagElements.removeClass().addClass("option-" + language);
                $("*[data-trans]").each(function() {
                    let $this = $(this);
                    let text = django.gettext(language, $this.attr('data-trans'));
                    let params = $this.attr('data-trans-params');
                    if (params) {
                        params = JSON.parse(params);
                        for (key in params) {
                            if (params.hasOwnProperty(key)) {
                                text = text.replace("{" + key + "}", params[key]);
                            }
                        }
                    }
                    this.innerText = text;
                });
                $.ajax({
                    url: "/language/",
                    method: "POST",
                    data: {
                        language: language,
                        csrftoken: $("input[name='csrfmiddlewaretoken']").val()
                    }
                });
            };
            $(this).change(update);
        });
        django.jsi18n_initialized = true;
    }
});
