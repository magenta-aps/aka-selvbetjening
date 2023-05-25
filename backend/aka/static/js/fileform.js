$(function(){
    // If all file rows are set (has a value), create a new empty row
    const updateRows = function(animate) {
        const form = $(this);
        const container = form.find(".file_container");
        const rows = container.find(".doc_file").not(".prototype");
        let allFilled = true;
        if (animate !== false) {
            animate = true;
        }
        rows.each(function() {
            const $this = $(this);
            const fileField = $this.find("input[type=file]");
            const filled = (fileField.val() !== undefined && fileField.val() !== '');
            $this.find("button").toggle(filled);
            if (!filled) {
                allFilled = false;
            }
        });
        if (allFilled) {
            const clone = container.find(".doc_file.prototype").first().clone();
            clone.removeClass("prototype");
            clone.find("input").val('');
            const m = /id_form-(\d+)-file_data/.exec(clone.find("input[type=file]").attr("id"));
            const form_index = m ? m[1] : $("form").index(form);
            const row_index = firstIdleIndex(container);
            const file_name = "form-"+form_index+"-file_data_"+row_index;
            clone.find("input[type=file]").attr({"id": "id_"+file_name, "name": file_name});
            const text_name = "form-"+form_index+"-file_description_"+row_index;
            clone.find("input[type=text]").attr({"id": "id_"+text_name, "name": text_name});
            clone.change(updateRows.bind(form));
            clone.find(".close").click(removeRow).hide();
            container.append(clone);
            if (animate) {
                clone.slideDown();
            } else {
                clone.show();
            }
        }
    }

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

    const firstIdleIndex = function(container) {
        const indexes = getRowIndexes(container);
        let i=0;
        while (indexes[""+i]) {
            i++;
        }
        return i;
    }

    const removeRow = function() {
        const row = $(this).parents(".doc_file");
        row.slideUp(400, function(){
            row.remove();
        });
    }

    $("form").each(function() {
        $(this).find(".doc_file").change(updateRows.bind(this));
        $(this).find(".doc_file .close").click(removeRow);
        updateRows.call(this, false);
    });

    $("form").submit(function() {
        $('.doc_file.prototype').remove();
    });

});
