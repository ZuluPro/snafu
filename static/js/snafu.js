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

  // POP OVER INIT
  $("[rel=popover]").popover({trigger:'hover'})

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

  // REF DETAILS
  $.fn.refDetail = function(){
    $.get('/snafu/configuration/ref',{ refPk:$(this).attr('pk') }, function(data) {
      $('#refContent').html(data);
    })
  }

  // MY REFERENCE FILTER
  $.fn.getReferences = function(){
    $('#refContent').html();
    $('#R_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/ref_q',{'q': $('#ref_q').val() }, function(data) {
      $('#R_tbody').html( data );
    });
  }

  // GET REF
  $.fn.getRef = function(pk){
    $('#refContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/ref/'+pk+'/get', function(data) {
      $('#refContent').html(data);
    })
  }

 // DEL REF
  $.fn.delRef = function(pk){
    $('#refContent').html('');
    $.post('/snafu/configuration/ref/'+pk+'/del',{ csrfmiddlewaretoken:$('input[name="csrfmiddlewaretoken"]').val() }, function(data) {
      $('#refCount').html(data)
      $('#ref'+pk+'Tab').hide('300');
    })
  }

 // GET ALERT
  $.fn.getAlertWithoutRef = function(pk){
    $('#refAlertContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/ref/alert/'+pk, function(data) {
      $('#refAlertContent').html(data);
    })
  }

 // GOTO ADDREF WITH AN Alert ATTR
  $.fn.getAlertRef = function(pk){
    $.get('/snafu/configuration/ref/alert/'+pk+'/form', {}, function(data) {
      $('#addRef').html(data)
      $('#addRefTab').tab('show')
    })
  }

 // TRANSFORM <p> INTO INPUT
 // $.fn.createInput = function(pk,attr,val){
 //   $('#refContent').html('');
 // }

});

