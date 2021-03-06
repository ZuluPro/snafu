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

  // RELOAD ALERTS
  $.fn.reloadAlerts = function(){
    $.ajax({ 
      type: "POST", 
      url: '/snafu/event/reloadAlerts', 
      data: $('[name=csrfmiddlewaretoken]:first').serialize(),
      async: true,
      cache: false,
      error: function() {
        $('#infoModal').html( 'Erreur de communication avec le serveur' );
        $('#infoModal').modal('show');
      },
      success: function(data) {
        $('#messages').hide();
        $('#messages').html( data );
        $('#messages').show(300);
      },
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

  // EVENTS FILTER
  $('input[filter]').change( function() {
    $('#E_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif">' );
    data = {
      'pk': $('#pk').val(),
      'element': $('#element').val(),
      'glpi' : $('#glpi').val(),
      'message' : $('#message').val(),
      'date' : $('#datepicker').val()
    };
    $.ajax({ 
      type: "GET", 
      url: '/snafu/event/filter',
      data: data,
      async: false,
      cache: false,
      error: function(data) {
        $('#infoModal').html("<center>Données demandées invalides !</center>");
        $('#infoModal').modal('show');
        $.get('/snafu/event/filter', function(data) {
          $('#E_tbody').html(data);
        });
      },
      success: function(data) { $('#E_tbody').html( data ); }
    })
  });

  // AGGREGATION MODAL
  $.fn.AgrForm = function(){
    ids = [];
    $('input:checked').each( function() {
      ids.push( $(this).val() );
    })
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

  // MAKE FORM 
  $.fn.update = function(model){
    if ( $('#'+model+'Content button[data-toggle=button].active').size() != 0 ) {
      POST = {};
      $('#'+model+'Content form :input').each( function() { POST[$(this).attr('name')] = $(this).val(); })
      $.ajax({ 
        type: "POST", 
        url: '/snafu/configuration/update', 
        data: POST,
        async: false,
        cache: false,
        error: function() {
          $('#infoModal').html( 'Erreur de communication avec le serveur' );
          $('#infoModal').modal('show');
        },
        success: function(data) {
          $('#'+model+'Content form p').show(150)
          $('#'+model+'Content form :input').hide(150)
        },
      });
    } else {
      $('#'+model+'Content form p').hide(150)
      $('#'+model+'Content form :input').show(150)
    }
  }

/////////////////////////////////////////
  // REF DETAILS
  $.fn.refDetail = function(){
    $.get('/snafu/configuration/ref',{ refPk:$(this).attr('pk') }, function(data) {
      $('#refContent').html(data);
    })
  }

  // MY REFERENCE FILTER
  $.fn.getReferences = function(page){
    $('#refContent').html();
    $('#R_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/ref_q', {
     'q': $('#ref_q').val(),
     'page':page
    }, function(data) {
      $('#R_tbody').html(data);
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
      $('#referenceTab').html(data)
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
      $('#addRef').html(data);
      $('#addRefTab').tab('show');
    })
  }

 // ADD A REF FROM FORM
  $.fn.addRef = function(){

    $.ajax({ 
      type: "POST", 
      url: '/snafu/configuration/ref/add', 
      data: $('#referenceForm').serialize(),
      async: false,
      cache: false,
      success: function(data, status, xhr) {
         $('#msg-info').hide();
         $('#msg-info').remove();

         var ct = xhr.getResponseHeader("content-type") || "";
         if (ct.indexOf('html') > -1) {
           $('#referenceTab').html(data);
           $('#add-ReferenceTab').tab('show');
         } else if (ct.indexOf('json') > -1) {
           var errors = JSON.parse(xhr.responseText);
           $('#referenceForm').prepend('<div id="msg-info" class="alert alert-error" style="display: block;"><h4>Erreur(s) de formulaire :</h4><p class="pull-right"><button class="close" onclick="$(\'#msg-info\').hide(250); return false;">×</button></p><ul id="msg-content"></ul></div>');
           for ( var k in errors) {
             $('#msg-content').append('<li><b>'+k+'</b> : '+errors[k]+'</li>');
           }
         }  
      },
      error: function() { alert('err'); }
    })
  }

 // GOTO ADDREF WITH AN Alert ATTR
  $.fn.getRefForm = function(type){
    if ( ! type ) { var type = 'simple'; }
    $.get('/snafu/configuration/ref/form/'+type, {}, function(data) {
      $('#add-referenceContent').html(data);
      $('#add-referenceTab').tab('show');
      $('#'+type+'Ref-tab').tab('show');
    })
  }

///////////////////////////////////////////////////////////
  // GET TRAD
  $.fn.getTrad = function(pk){
    $('#tradContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/trad/'+pk+'/get', function(data) {
      $('#tradContent').html(data);
    })
  }

  // TRADUCTION FILTER
  $.fn.getTraductions = function(page){
    $('#tradContent').html();
    $('#T_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/trad_q', {
     'q': $('#trad_q').val(),
     'page':page
    }, function(data) {
      $('#T_tbody').html(data);
    });
  }

 // GET ALERTS WITHOUT REF
  $.fn.getAsWithoutTrad = function(page){
    $('#tradAlerts').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/trad/alert/tabs', { 
     'q': $('#a_trad_q').val(),
     'page': page
    }, function(data) {
      $('#tradAlerts').html(data);
    });
  }

 // GOTO ADDREF WITH AN Alert ATTR
  $.fn.getAlertTrad = function(pk){
    $.get('/snafu/configuration/trad/alert/'+pk+'/form', {}, function(data) {
      $('#addTradContent').html(data)
      $('#addTradTab').tab('show')
    })
  }

 // ADD A TRAD FROM FORM
  $.fn.addTrad = function(){

    if ( ! $('#tradForm input[name="id"]').val() ) { var trad_id = 0; }
    else { var trad_id = $('#tradForm input[name="id"]').val(); };

    $.ajax({ 
      type: "POST", 
      url: '/snafu/configuration/trad/'+trad_id+'/add', 
      data: $('#tradForm').serialize(),
      async: false,
      cache: false,
      success: function(data) {
         $('#traductionTab').html(data);
      },
      error: function() { alert('err'); }
    })
  }

  $('#tradForm').submit(function() {
    $.fn.addTrad();
    return false;
  });

 // DEL TRAD
  $.fn.delTrad = function(pk){
    $('#tradContent').html('');
    $.post('/snafu/configuration/trad/'+pk+'/del',{ csrfmiddlewaretoken:$('input[name="csrfmiddlewaretoken"]').val() }, function(data) {
      $('#traductionTab').html(data)
      $('#trad'+pk+'Tab').hide('300');
    })
  }
///////////////////////////////////////////////////////////

  $.fn.snafu_object = function(action, object, pk) {
    if ( ! pk ) { pk = 0; }
    if ( action == "get" ) {
      $('#'+object+'Content').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
      $.get('/snafu/configuration/get/'+object+'/'+pk, function(data) {
        $('#'+object+'Content').html(data);
      });

    } else if ( action == "del" ) {
      $('#'+object+'Content').children().hide(250);
      $('#'+object+'Content').html('');
      $.post('/snafu/configuration/del/'+object+'/'+pk,{ csrfmiddlewaretoken:$('input[name="csrfmiddlewaretoken"]').val() }, function(data) {
        $('#'+object+'Tab').html(data);
        $('#'+object+pk+'Tab').hide('300');
      });

    } else if ( action == "list" ) {
      $('#'+object+'Content').html();
      $('#'+object+'-ul').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
      request = { 'q': $('#'+object+'_q').val(), 'page': pk };
      $.get('/snafu/configuration/list/'+object, request, function(data) {
        $('#'+object+'-ul').html( data );
      });

    } else if ( action == "form" ) {
      $.get('/snafu/configuration/form/'+object+'/'+pk, {}, function(data) {
        if ( object == "a_translation" ) { object = "translation"; }
        else if ( object == "a_reference" ) { object = "reference"; }
        $('#add-'+object+'Content').html(data);
        $('#add-'+object+'Tab').tab('show');
      });

    } else if ( action == "add" ) {
      $('#'+object+'Content').html('');

      if ( ! $('#'+object+'Form input[name="id"]').val() ) { var temp_id = 0; }
      else { var temp_id = $('#'+object+'Form input[name="id"]').val(); };

      $.ajax({ 
        type: "POST", 
        url: '/snafu/configuration/add/'+object+'/'+temp_id, 
        data: $('#'+object+'Form').serialize(),
        async: false,
        cache: false,
        success: function(data, status, xhr) {
           $('#msg-info').hide();
           $('#msg-info').remove();

           var ct = xhr.getResponseHeader("content-type") || "";
           if (ct.indexOf('html') > -1) {
             $('#'+object+'Tab').html(data);
             $('#add-'+object+'Tab').tab('show');
           } else if (ct.indexOf('json') > -1) {
             var errors = JSON.parse(xhr.responseText);
             $('#'+object+'Form').prepend('<div id="msg-info" class="alert alert-error" style="display: block;"><h4>Erreur(s) de formulaire :</h4><p class="pull-right"><button class="close" onclick="$(this).parent().parent().hide(250); return false;">×</button></p><ul id="msg-content"></ul></div>');
             for ( var k in errors) {
               $('#msg-content').append('<li><b>'+k+'</b> : '+errors[k]+'</li>');
             }
            // $.fn.msg_box(xhr.responseText, '#'+object+'Form')
           }  
        },
        error: function() { alert('err'); }
      });
    } else if ( action == "update" ) {
      if ( $('#'+object+'Content button[data-toggle=button].active').size() != 0 ) {
        POST = {};
        $('#'+object+'Content form :input').each( function() { POST[$(this).attr('name')] = $(this).val(); })
        $.ajax({ 
          type: "POST", 
          url: '/snafu/configuration/update/'+object+'/'+pk, 
          data: $('#'+object+'Content form :input').serialize(),
          async: true,
          cache: false,
          error: function() {
            $('#infoModal').html( 'Erreur de communication avec le serveur' );
            $('#infoModal').modal('show');
          },
          success: function(data, status, xhr) {
            var ct = xhr.getResponseHeader("content-type") || "";
            if (ct.indexOf('html') > -1) {
              $.fn.snafu_object('get',object,pk);
            } else if (ct.indexOf('json') > -1) {
              var errors = JSON.parse(xhr.responseText);
              $('#'+object+'Form').prepend('<div id="msg-info" class="alert alert-error" style="display: block;"><h4>Erreur(s) de formulaire :</h4><p class="pull-right"><button class="close" onclick="$(this).parent().parent().hide(250); return false;">×</button></p><ul id="msg-content"></ul></div>');
              for ( var k in errors) {
                $('#msg-content').append('<li><b>'+k+'</b> : '+errors[k]+'</li>');
              }
              $('#'+object+'Content button[data-toggle=button]').addClass('active');
            }
          }
        });
      } else {
        $.ajax({ 
          type: "GET",
          url: '/snafu/configuration/form/'+object+'/'+pk,
          async: true,
          error: function() {
            $('#infoModal').html('Erreur de communication avec le serveur');
            $('#infoModal').modal('show');
          },
          success: function(data) {
            $('#'+object+'Content dl').html(data);
            $('#'+object+'Content button[class="btn"]').show(200); 
            $('#'+object+'Content form button').hide();
          }
        });
      }
    }
  }

//////////////////////////////////////////////////

 // ASK QUESTION BEFORE LAUNCH FUNCTION
  $.fn.Question = function(question, func){
    $('#infoModal').modal('hide');
    $('#infoModal').html(question, func);
  }

});
