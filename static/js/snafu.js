$(document).ready(function() {

  // USE AJAX GET AND #infoModal
  $.fn.UseModal = function(url,GETdict){
    $('#infoModal').modal('hide')
    $.ajax({ 
      type: "GET", 
      url: url, 
      data: GETdict,
      async: false,
      cache: false,
      error: function() {
        $('#infoModal').html( 'Erreur de communication avec le serveur' );
      },
      success: function(data) {
        $('#infoModal').html( data );
      },
      complete: function() {
        $('#infoModal').modal('toggle');
      }
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
    $('input:not(#infoModal input)').attr('checked',false);
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

 // GET ALERT WITHOUT REF
  $.fn.getAlertWithoutRef = function(pk){
    $('#refAlertContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/ref/alert/'+pk, function(data) {
      $('#refAlertContent').html(data);
    })
  }

 // GET ALERTS WITHOUT REF
  $.fn.getAsWithoutRef = function(){
    $('#refAlerts').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/ref/alert/tabs', { q : $('#a_ref_q').val() }, function(data) {
      $('#refAlerts').html(data);
    });
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

  // MY REFERENCE FILTER
  $.fn.getUsers = function(){
    $('#userContent').html();
    $('#U_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/user_q',{'q': $('#user_q').val() }, function(data) {
      $('#U_tbody').html( data );
    });
  }

  // GET USER
  $.fn.getUser = function(pk){
    $('#userContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/user/'+pk+'/get', function(data) {
      $('#userContent').html(data);
    })
  }

 // DEL A USER FROM FORM
  $.fn.delUser = function(pk){
    $('#userContent').html('');
    $.post('/snafu/configuration/user/'+pk+'/del',{ csrfmiddlewaretoken:$('input[name="csrfmiddlewaretoken"]').val() }, function(data) {
      $('#userCount').html(data);
      $('#user'+pk+'Tab').hide('300');
    })
  }

 // ADD A USER FROM FORM
  $.fn.addUser = function(){
    $('#userContent').html('');
      $.ajax({ 
        type: "POST", 
        url: '/snafu/configuration/user/'+$('#userForm input[name="id"]').val()+'/add', 
        data: $('#userForm').serialize(),
        async: false,
        cache: false,
        success: function(data) {
           $('#userCount').html(data);
           $('#userForm input').val('');
        },
        error: function() { alert('err'); }
      })
  }

  $('#userForm').submit(function() {
    $.fn.addUser();
    return false;
  });

 // ASK QUESTION BEFORE LAUNCH FUNCTION
  $.fn.Question = function(question, func){
    $('#infoModal').modal('hide');
    $('#infoModal').html(question, func);
  }

});

