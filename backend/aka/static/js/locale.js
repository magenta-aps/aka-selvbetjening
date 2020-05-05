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

        const format = django.format = function(text, params, language) {
            if (typeof text !== 'string') {
                text = String(text);
            }
            text = django.gettext(language, text);
            if (params) {
                for (let key in params) {
                    if (params.hasOwnProperty(key)) {
                        let value = params[key];
                        if (Array.isArray(value)) {
                            // If a value is an array, it must be [message:string, params:dict]
                            value = format(value[0], value[1], language);
                        } else {
                            value = format(value, null, language);
                        }
                        text = text.replace("{" + key + "}", value);
                    }
                }
            }
            return text.replace("&amp;", "&");
        };

        const localeChanger = $("*[data-locale-changer]");
        localeChanger.each(function(){
            const langChooser = $(this);
            const flagElements = $(langChooser.attr("data-locale-flag"));
            const update = function(){
                const language = $(this).val();
                flagElements.removeClass().addClass("option-" + language);
                django.language = language;
                $(document).trigger('language-change', language);
            };
            $(this).change(update);
        });
        django.jsi18n_initialized = true;
        django.language = localeChanger.val();

        const $document = $(document);
        $document.on('language-change', function(event, language) {
            $.ajax({
                url: "/language/",
                method: "POST",
                data: {
                    language: language,
                    csrftoken: $("input[name='csrfmiddlewaretoken']").val()
                }
            });
        });
        $document.on('language-change', function(event, language) {
            $("*[data-trans]").each(function() {
                let $this = $(this);
                let text = $this.attr('data-trans');
                let params = $this.attr('data-trans-params');
                text = format(text, params && JSON.parse(params), language);
                this.innerHTML = text;
            });
        });


    }
});
