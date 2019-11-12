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
});
