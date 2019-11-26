$(function(){

    kl = {
        months: ['a01','a02','a03','a04','a05','a06','a07','a08','a09','a10','a11','a12'],
        dayOfWeekShort: ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7'],
        dayOfWeek: ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7'],
    };

    $.datetimepicker.addLocale(
        'kl',
        ['Januaari','Februaari','Marsi','Apriili','Maaji','Juuni','Juuli','Aggusti','Septembari','Oktobari','Novembari','Decembari'],
        ['Ata', 'Mar', 'Pin', 'Tal', 'Sis', 'Arf', 'Sap'],
        ['Ataasinngorneq', 'Marlunngorneq', 'Pingasunngorneq', 'Tallimanngorneq', 'Sisamanngorneq', 'Arfininngorneq', 'Sapaat'],
    );

    $(".datepicker").datetimepicker({timepicker:false, format:'d/m/Y'});

    $.datetimepicker.setLocale('kl');
});

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
});

$(function(){
    const container = $("#codebitorContainer");
    const codebtorFormset = container.formset("form", $("#codebitorFormsetPrototype"));

    const updateRows = function() {
        // Checks the existing rows. If no rows are empty, add another row. If more than one row is empty, remove the last empty row
        let emptyCount = 0;
        let lastEmpty = null;
        container.find('.subform-row').each(function () {
            let thisEmpty = true;
            $(this).find("input").each(function(){
                if (this.value) {
                    thisEmpty = false;
                }
            });
            if (thisEmpty) {
                emptyCount++;
                lastEmpty = $(this);
            }
        });
        if (emptyCount === 0) {
            codebtorFormset.addForm();
        } else if (emptyCount > 1) {
            codebtorFormset.removeForm(lastEmpty);
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
