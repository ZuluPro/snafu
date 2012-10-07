$(document).ready(function() {

  // USE AJAX GET AND #infoModal
  $.fn.UseModal = function(url,GETdict){
    $.get(url,GETdict, function(data) {
      $('#infoModal').html( data );
      $('#infoModal').modal('toggle')
    });
  }

  // USE AJAX POST IN #infoModal
  $.fn.PostModal = function(){
    $.ajax({ 
      type: "POST", 
      url: $('#formModal').attr("action"), 
      data: $('#formModal').serialize(),
      async: false,
      cache: false,
      error: function() { alert('err'); },
      })
    $('#infoModal').modal('hide')
    } 

  // TO CLEAR MODAL AFTER USE
  $('#infoModal').on('hidden', function () {
    $(this).text('')
  })

  // MY EVENTS FILTER
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

  // AGGREGATION MODAL
  $.fn.AgrForm = function(){
    ids = [];
    $('input:checked').each( function(box) { ids.push( $(this).val() )})
    $.fn.UseModal('/eventsAgr', { events: ids } )
    $('input').attr('checked',false);
  }

  // AGGREGATION MODAL
  $.fn.CPAForm = function(){
    $.fn.UseModal('/events/choosePrimaryAlert', { eventPk: $('input:checked').val() } )
    $('input').attr('checked',false);
  }


});

