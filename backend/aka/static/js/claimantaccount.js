$(function(){
    $('th.sortable').each(function(){
        const th = $(this),
            table = th.parents("table").first();
        let thIndex = th.index(),
            inverse = false;
        th.click(function(){
            const $this = $(this);
            inverse = !inverse;
            table.find('td').filter(function(){
                return $(this).index() === thIndex;
            }).sortElements(function(a, b) {
                const $a = $(a), $b = $(b);
                const aValue = $a.attr('data-raw') || $a.text();
                const bValue = $b.attr('data-raw') || $b.text();
                if (aValue === bValue) {
                    return 0;
                }
                return aValue > bValue ?
                    inverse ? -1 : 1
                    : inverse ? 1 : -1;
            }, function(){
                return this.parentNode;
            });
            $this.addClass("sorted").toggleClass("asc", inverse).toggleClass("desc", !inverse);
            table.find("th").not($this).removeClass("sorted asc desc");
        });
    });
});
