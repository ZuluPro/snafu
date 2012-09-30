$(document).ready(function() {

  $.fn.AgrForm = function(){
    ids = [];
    $('input:checked').each( function(box) { ids.push( $(this).val() )})
    $.get('/eventsAgr', { events: ids }, function(data) {
      $('#infoModal').html( data );
      $('#infoModal').modal('toggle');
    });
    ids.length = 0;
  }
});

