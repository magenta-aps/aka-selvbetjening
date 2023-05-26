$(function(){
    $.fn.extend({
        'formset': function(name, formPrototypeContainer) {
            const management = {
                total: $('#id_'+name+'-TOTAL_FORMS'),
                initial: $('#id_'+name+'-INITIAL_FORMS'),
                min: $('#id_'+name+'-MIN_NUM_FORMS'),
                max: $('#id_'+name+'-MAX_NUM_FORMS')
            };
            const formContainer = this;
            const formPrototype = formPrototypeContainer.children().first();
            const rowclass = formContainer.data("formset-rowclass") || "row";

            const updateTotal = function() {
                management.total.val(formContainer.children().not(formPrototypeContainer).length);
            };

            const addForm = function(update, animate) {
                const form = formPrototype.clone();
                const nextId = parseInt(management.total.val());
                form.find('*').each(function() {
                    for (let i = 0; i < this.attributes.length; i++) {
                        this.attributes[i].nodeValue = this.attributes[i].nodeValue.replace('__prefix__', nextId);
                    }
                });
                form.hide();
                formContainer.append(form);
                if (update !== false) {
                    updateTotal();
                }
                if (animate) {
                    form.slideDown();
                } else {
                    form.show();
                }
                updateRemoveButtons();
                return form;
            };

            const removeForm = function(form, update, animate) {
                if (!form) {
                    form = $(this).parents("."+rowclass);
                }
                if (form.parent().first().is(formContainer)) {
                    const next = function () {
                        form.remove();
                        if (update !== false) {
                            updateTotal();
                        }
                        updateRemoveButtons();
                    };
                    if (animate) {
                        form.slideUp({"complete": next});
                    } else {
                        next();
                    }
                }
            };

            const updateRemoveButtons = function() {
                const rows = formContainer.find("."+rowclass).not(formPrototype);
                rows.find("[data-formset-button=deleterow]").toggle(rows.length > 1);
            }

            const rowFilled = function(row) {
                const significantFields = row.find(
                    "input[data-formset-update]," +
                    "select[data-formset-update]," +
                    "[data-formset-update] input," +
                    "[data-formset-update] select"
                );
                let thisRowFilled = false;
                significantFields.each(function () {
                    if (this.value !== undefined && this.value !== '') {
                        thisRowFilled = true;
                        return false;
                    }
                });
                return thisRowFilled;
            };

            const updateRows = function(animate) {
                const rows = formContainer.find("."+rowclass).not(formPrototype);
                let allRowsFilled = true;
                if (animate !== false) {
                    animate = true;
                }
                rows.each(function() {
                    const row = $(this);
                    const thisRowFilled = rowFilled(row);
                    if (!thisRowFilled) {
                        allRowsFilled = false;
                        return false;
                    }
                });
                if (allRowsFilled) {
                    const newform = addForm(true, animate);
                    newform.find("input,select").change(updateRows);
                    newform.find("[data-formset-button=deleterow]").click(function () {
                        removeForm.call(this, null, true, true);  // Do not pass event to method
                    });
                }
            }

            if (formContainer.data("auto-add")) {
                this.find("input,select").change(updateRows);
            }
            formContainer.find("[data-formset-button=deleterow]").click(function () {
                removeForm.call(this, null, true, true);  // Do not pass event to method
            });
            updateRemoveButtons();

            return {
                'addForm': addForm,
                'removeForm': removeForm
            }
        }
    });

    $(function () {

        const getRowIndexes = function(container) {
            const indexes = {};
            container.find(".doc_file").not(".prototype").each(function(){
                const id = $(this).find("input[type=file]").attr("id");
                const s = id.lastIndexOf("_");
                if (s !== -1) {
                    indexes[id.substring(s+1)] = $(this);
                }
            });
            return indexes;
        };

        $("[data-formset]").each(function() {
            const container = $(this);
            container.formset(container.data("formset"), container.find(".prototype"));
        });

        $("form").submit(function() {
            $('[data-formset] .prototype').remove();
        });

    });
});

