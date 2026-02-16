const tables = {};
const fixedColsSettings = [3, 1, 2]; // First, second, third tab

$(document).ready(function () {
{% for sheet_name, sheet in sheets.items() %}  
  tables["{{ loop.index0 }}"] = $('#table_{{ loop.index0 }}').DataTable({
    scrollX: true,
    scrollY: '70vh',
    scrollCollapse: true,
    paging: false,
    autoWidth: false,
    dom: 'Bfrtip',
    buttons: [
      { extend: 'csvHtml5', text: 'Download CSV', title: '{{ sheet_name }}', exportOptions: { columns: ':visible' }, className:'dt-button' }
    ],
    fixedColumns: {
        leftColumns: fixedColsSettings[{{ loop.index0 }}]   // <-- freeze the first 2 columns
    }      
  });
   
   // Move search label into placeholder
    var search_input = $('#table_{{ loop.index0 }}_filter input');
    search_input.attr('placeholder', 'Search...');
    $('#table_{{ loop.index0 }}_filter label').contents().filter(function(){ return this.nodeType === 3; }).remove();

  {% endfor %}

  function adjustAll() {
    $.fn.dataTable.tables({ visible: true, api: true })
      .columns.adjust();
  }

  $('.tab-button').on('click', function () {
    const id = $(this).data('tab');

    $('.tab-button').removeClass('active');
    $(this).addClass('active');
    $('.tab-content').removeClass('active');
    $('#tab_' + id).addClass('active');

    setTimeout(adjustAll, 50);
  });

  $('#sidebarToggle').on('click', function () {
    $('#sidebar').toggleClass('collapsed');
    setTimeout(adjustAll, 300);
  });

  $(window).on('resize', () => {
    adjustAll();
  });
});