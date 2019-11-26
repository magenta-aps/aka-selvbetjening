$(function(){
    $.ajax({
        url: "static/json/fordringsgruppe.json",
        success: function(groups){
            const groupSelect = $("#id_fordringsgruppe");
            const typeSelect = $("#id_fordringstype");
            group_dict = {};
            for (let i=0; i<groups.length; i++) {
                let group = groups[i];
                group_dict[group['id']] = group;
            }
            const updateType = function(){
                let group = group_dict[this.value];
                typeSelect.empty();
                for (let i=0; i<group['sub_groups'].length; i++) {
                    let subGroup = group['sub_groups'][i];
                    let option = $("<option>");
                    option.attr("value", subGroup['group_id'] + "." + subGroup['type_id']);
                    option.text(subGroup['name']);
                    typeSelect.append(option);
                }
            };
            groupSelect.change(updateType);
            groupSelect.each(updateType);
        }
    });

});

$(function(){
    const documentationContainer = $("#documentationContainer");
    let documentationCounter = 0;
    $("#addDocumentationRow").click(function(){
        const field = $("<input>");
        field.attr({"type": "file", "name": "documentation"+(++documentationCounter)});
        documentationContainer.append(field);
    });

    const updateDocumentationFileFields = function(){
        const emptyFields = documentationContainer.find('input[type=file]').filter(function() {
            return !this.value;
        });
        if (emptyFields.length === 0) {
            const field = $("<input>");
            field.attr({"type": "file", "name": "documentation"+(++documentationCounter)});
            documentationContainer.append(field);
        } else if (emptyFields.length > 1) {
            emptyFields.last().delete();
        }
    };

    documentationContainer.on('change', 'input[type=file]', null, updateDocumentationFileFields);

});

$(function(){
    const container = $("#codebitorContainer");
    const codebtorFormset = container.formset("form", $("#codebitorFormsetPrototype"));

    const updateRows = function() {
        // Checks the existing rows. If no rows are empty, add another row. If more than one row is empty, remove the last empty row
        const emptyRows = container.find('.subform-row').filter(function() {
            // Check the number of fields with values in them. The row is empty if that number is 0
            return ($(this).find('input[type="text"]').filter(function() {
                return !!this.value;
            }).length === 0);
        });
        if (emptyRows.length === 0) {
            codebtorFormset.addForm();
        } else if (emptyRows.length > 1) {
            codebtorFormset.removeForm(emptyRows.last());
        }
    };
    const updateRow = function() {
        // Disable the empty field in a row when the other field is written in
        const $this = $(this);
        const sibling = $this.parents(".subform-field").siblings().first().find("input");
        if ($this.val() && !sibling.val()) {
            sibling.attr("disabled", "disabled");
        } else {
            sibling.removeAttr("disabled");
        }
    };
    container.find("input").each(updateRow);
    container.on("change keyup paste", "input", null, function(){
        // Defer updating until fields have been updated with values
        setTimeout(function(){
            updateRow.call(this);
            updateRows();
        }.bind(this), 0);
    });
});
