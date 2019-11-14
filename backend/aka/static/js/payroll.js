$(function(){
    const management = {
        total: $('#id_form-TOTAL_FORMS'),
        initial: $('#id_form-INITIAL_FORMS'),
        min: $('#id_form-MIN_NUM_FORMS'),
        max: $('#id_form-MAX_NUM_FORMS')
    };
    const formContainer = $('#formsetContainer');
    const formPrototype = $('#formsetPrototype').children().first();
    const addRow = $('#add-row');

    const addForm = function(updateTotal) {
        const form = formPrototype.clone();
        const nextId = parseInt(management.total.val());
        form.find('*').each(function () {
            for (let i = 0; i < this.attributes.length; i++) {
                this.attributes[i].nodeValue = this.attributes[i].nodeValue.replace('__prefix__', nextId);
            }
        });
        formContainer.append(form);
        if (updateTotal !== false) {
            management.total.val(nextId + 1);
        }
    };

    addRow.click(addForm);

    const validators = {
        'sum-match': function(field, matchFields) {
            let sum = 0;
            matchFields.each(function() {
                sum += parseFloat(this.value);
            });
            return sum === parseFloat(field.val());
        }
    };

    const form = $("#mainform");
    form.submit(function(event){
        let errors = {};

        var field = $("#id_total_amount");
        field.each(function() {
            if (!validators['sum-match']($(this), formContainer.find('input[name$="-amount"]'))) {
                errors[this.id] = ['loentraek.sum_mismatch'];
            }
        });

        if (Object.keys(errors).length) {
            event.preventDefault();
            for (field in errors) {
                if (errors.hasOwnProperty(field)) {
                    const fieldContainer = $('[data-field="'+field+'"]');
                    let errorList = fieldContainer.find("err-msg");
                    errorList.empty();
                    for (let i = 0; i < errors[field].length; i++) {
                        let item = $("<li>");
                        let error = errors[field][i];
                        item.attr("data-trans", error);
                        item.text(django.gettext(django.language, error));
                        errorList.append(item);
                    }
                    fieldContainer.addClass("has-error");
                }
            }
            return false;
        }
    });
});
