// =============================================
// CSAPI — TABLE.JS
// DataTables init + tab switching.
// Loaded with defer after jQuery + DataTables
// CDN scripts — jQuery's $(document).ready
// handles the timing correctly.
// =============================================

const FIXED_COLS = [3, 1, 2]; // left-frozen columns per tab index

$(document).ready(function () {
    const tables = {};

    // Init a DataTable for every .tab-content table
    $('.tab-content').each(function () {
        const idx  = $(this).attr('id').replace('tab_', '');
        const $tbl = $(`#table_${idx}`);
        if (!$tbl.length) return;

        tables[idx] = $tbl.DataTable({
            scrollX:      true,
            scrollY:      '70vh',
            scrollCollapse: true,
            paging:       false,
            info:         false,
            lengthChange: false,
            autoWidth:    false,
            dom:          'Bfrtip',
            buttons: [
                {
                    extend:        'csvHtml5',
                    text:          'Download CSV',
                    title:         $tbl.closest('.tab-content').data('sheet-name') || `sheet_${idx}`,
                    exportOptions: { columns: ':visible' },
                    className:     'button',
                },
            ],
            fixedColumns: {
                leftColumns: FIXED_COLS[parseInt(idx)] ?? 1,
            },
        });

        // Remove the "Search:" text label, keep only the input
        $(`#table_${idx}_filter input`).attr('placeholder', 'Search...');
        $(`#table_${idx}_filter label`)
            .contents()
            .filter(function () { return this.nodeType === 3; })
            .remove();
    });

    // Adjust all visible table column widths
    function adjustAll() {
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
    }

    // Tab switching
    $('.tab-button').on('click', function () {
        const id = $(this).data('tab');
        $('.tab-button').removeClass('active');
        $(this).addClass('active');
        $('.tab-content').removeClass('active');
        $(`#tab_${id}`).addClass('active');
        setTimeout(adjustAll, 50);
    });

    // Sidebar toggle (if present on this page)
    $('#sidebarToggle').on('click', function () {
        $('#sidebar').toggleClass('collapsed');
        setTimeout(adjustAll, 300);
    });

    $(window).on('resize', adjustAll);
});