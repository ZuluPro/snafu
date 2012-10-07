$(document).ready(function() {

  $.fn.UseModal = function(url,GETdict){
  $.get(url,GETdict, function(data) {
       $('#infoModal').html( data );
       $('#infoModal').modal('toggle')
     });
  }

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
    $.fn.UseModal('/eventsAgr', { events: ids } )
    ids.length = 0;
  }


});

