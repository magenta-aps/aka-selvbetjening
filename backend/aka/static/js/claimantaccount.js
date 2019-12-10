$(function(){

    const table = $(".folder-table");

    const findIndex = function(selector, index) {
        return selector.filter(function(){
            return $(this).index() === index;
        });
    };

    const sort = function(index, asc) {
        const th = findIndex(table.find("th"), index);
        const tds = findIndex(table.find("td"), index);
        tds.sortElements(function(a, b) {
            const $a = $(a), $b = $(b);
            const aValue = $a.attr('data-raw') || $a.text();
            const bValue = $b.attr('data-raw') || $b.text();
            if (aValue === bValue) {
                return 0;
            }
            return aValue > bValue ? (asc ? 1 : -1) : (asc ? -1 : 1);
        }, function(){
            return this.parentNode;
        });
        th.addClass("sorted").toggleClass("asc", asc).toggleClass("desc", !asc);
        table.find("th").not(th).removeClass("sorted asc desc");
        document.location.hash = "sort=" + index + "|" + (asc ? "asc":"desc");
    };

    $('th.sortable').each(function(){
        const th = $(this);
        let thIndex = th.index(),
            asc = false;
        th.click(function(){
            const $this = $(this);
            asc = !asc;
            sort(thIndex, asc);
        });
    });

    if (document.location.hash) {
        const match = /sort=(\d+)\|(asc|desc)/.exec(document.location.hash);
        if (match) {
            const index = parseInt(match[1]),
                direction = match[2];
            if (!isNaN(index) && direction) {
                sort(index, direction !== 'desc');
            }
        }
    }
});
