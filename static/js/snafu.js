$(document).ready(function() {

    $('input[filter]').change( function() {
            $.get('/events/filter',
                {
                    'pk': $('#pk').val(),
                    'element': $('#element').val(),
                    'glpi' : $('#glpi').val(),
                    'message' : $('#message').val(),
                    'date' : $('#datepicker').val()
                }, function(data) {
                $('#E_tbody').html( data );
            })
    });

  $.fn.AgrForm = function(){
    ids = [];
    $('input:checked').each( function(box) { ids.push( $(this).val() )})
    $.get('/eventsAgr', { events: ids }, function(data) {
      $('#infoModal').html( data );
      $('#infoModal').modal('toggle');
    });
    ids.length = 0;
  }

  $.fn.UseModal = function(url,eventPk){
  $.get(url,{ eventPk: eventPk }, function(data) {
       $('#infoModal').html( data );
       $('#infoModal').modal('toggle')
     });
  }

});

