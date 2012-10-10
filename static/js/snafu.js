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
    $('#E_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif">' );
    $.get('/snafu/event/filter',
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
    $('input:checked').each( function() { ids.push( $(this).val() )})
    $.fn.UseModal('/snafu/event/agr', { events: ids } )
    $('input').attr('checked',false);
  }

  // PRIMARY ALERT MODAL
  $.fn.CPAForm = function(){
    $.fn.UseModal('/snafu/event/choosePrimaryAlert', { eventPk: $('input:checked').val() } )
    $('input').attr('checked',false);
  }

  // CLOSE MODAL
  $.fn.CloseForm = function(){
    ids = [];
    $('input:checked').each( function() { ids.push( $(this).val() )})
    $.fn.UseModal('/snafu/event/close', { events: ids } )
    $('input').attr('checked',false);
  }

  // FOLLOW-UP MODAL
  $.fn.FollowUpForm = function(){
    $.fn.UseModal('/snafu/event/followup', { eventPk: $('input:checked').val() } )
    $('input').attr('checked',false);
  }


});

