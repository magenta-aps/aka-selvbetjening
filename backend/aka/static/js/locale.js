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
                return (count == 1) ? singular : plural;
            } else {
                return value.constructor === Array ? value[django.pluralidx(count)] : value;
            }
        };

        django.gettext_noop = function(msgid) { return msgid; };

        django.pgettext = function(language, context, msgid) {
            var value = django.gettext(language, context + '\x04' + msgid);
            if (value.indexOf('\x04') != -1) {
                value = msgid;
            }
            return value;
        };

        django.npgettext = function(language, context, singular, plural, count) {
            var value = django.ngettext(language, context + '\x04' + singular, context + '\x04' + plural, count);
            if (value.indexOf('\x04') != -1) {
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

        globals.pluralidx = django.pluralidx;
        globals.gettext = django.gettext;
        globals.ngettext = django.ngettext;
        globals.gettext_noop = django.gettext_noop;
        globals.pgettext = django.pgettext;
        globals.npgettext = django.npgettext;
        globals.interpolate = django.interpolate;


        const getLanguage = function(language, cb) {
            if (window.django.catalog[language] !== undefined) {
                cb(window.django.catalog[language]);
            }
            $.ajax({
                url: "/language/"+language,
                dataType: "json",
                success: function(response, textStatus, jqXHR) {
                    window.django.catalog[language] = response
                },
                error: function() {
                    window.django.catalog[language] = {};
                },
                complete: cb
            });
        };

        $("*[data-locale-changer]").each(function(){
            const langChooser = $(this);
            const flagElements = $(langChooser.attr("data-locale-flag"));
            const update = function(){
                const language = $(this).val();
                const doUpdate = function() {
                    flagElements.removeClass().addClass("option-" + language);
                    $("*[data-trans]").each(function () {
                        this.innerText = gettext(language, $(this).attr('data-trans'));
                    });
                };
                if (window.django.catalog[language]) {
                    doUpdate();
                } else {
                    getLanguage(language, doUpdate);
                }
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
