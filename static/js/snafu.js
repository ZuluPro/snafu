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
    $('#userContent').html('');

    if ( ! $('#refForm input[name="id"]').val() ) { var ref_id = 0; }
    else { var ref_id = $('#refForm input[name="id"]').val(); };

    $.ajax({ 
      type: "POST", 
      url: '/snafu/configuration/ref/'+ref_id+'/add', 
      data: $('#refForm').serialize(),
      async: false,
      cache: false,
      success: function(data) {
         $('#referenceTab').html(data);
      },
      error: function() { alert('err'); }
    })
  }

  $('#refForm').submit(function() {
    $.fn.addRef();
    return false;
  });

 // TRANSFORM <p> INTO INPUT
 // $.fn.createInput = function(pk,attr,val){
 //   $('#refContent').html('');
 // }


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

 // GET ALERT WITHOUT REF
  $.fn.getAlertWithoutTrad = function(pk){
    $('#tradAlertContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/trad/alert/'+pk, function(data) {
      $('#tradAlertContent').html(data);
    })
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

 // ADD A REF FROM FORM
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

///////////////////////////////////////////////////////////
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

  // MY USER FILTER
  $.fn.getUsers = function(){
    $('#userContent').html();
    $('#U_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/user_q',{'q': $('#user_q').val() }, function(data) {
      $('#U_tbody').html( data );
    });
  }

 // GOTO ADDUSER
  $.fn.getUserForm = function(){
    $.get('/snafu/configuration/user/form', {}, function(data) {
      $('#addUser').html(data)
      $('#addUserTab').tab('show')
    })
  }

 // ADD A USER FROM FORM
  $.fn.addUser = function(){
    $('#userContent').html('');

    if ( ! $('#userForm input[name="id"]').val() ) { var user_id = 0; }
    else { var user_id = $('#userForm input[name="id"]').val(); };

    $.ajax({ 
      type: "POST", 
      url: '/snafu/configuration/user/'+user_id+'/add', 
      data: $('#userForm').serialize(),
      async: false,
      cache: false,
      success: function(data) {
         $('#userTab').html(data);
      },
      error: function() { alert('err'); }
    })
  }

  $('#userForm').submit(function() {
    $.fn.addUser();
    return false;
  });

//////////////////////////////////////////////////

  // GET HOST
  $.fn.getHost = function(pk){
    $('#hostContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/host/'+pk+'/get', function(data) {
      $('#hostContent').html(data);
    })
  }

  // MY HOST FILTER
  $.fn.getHosts = function(){
    $('#hostContent').html();
    $('#Ho_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/host_q',{'q': $('#host_q').val() }, function(data) {
      $('#Ho_tbody').html( data );
    });
  }

 // GOTO ADDUSER
  $.fn.getHostForm = function(){
    $.get('/snafu/configuration/host/form', {}, function(data) {
      $('#addHostContent').html(data)
      $('#addHostTab').tab('show')
    })
  }

 // ADD A USER FROM FORM
  $.fn.addHost = function(){
    $('#hostContent').html('');

    if ( ! $('#hostForm input[name="id"]').val() ) { var host_id = 0; }
    else { var host_id = $('#hostForm input[name="id"]').val(); };

    $.ajax({ 
      type: "POST", 
      url: '/snafu/configuration/host/'+host_id+'/add', 
      data: $('#hostForm').serialize(),
      async: false,
      cache: false,
      success: function(data) {
         $('#glpihostTab').html(data);
         $('#HostListTab').tab('show');
      },
      error: function() { alert('err'); }
    })
  }

  $('#hostForm').submit(function() {
    $.fn.addHost();
    return false;
  });

 // DEL HOST
  $.fn.delHost = function(pk){
    $('#HostContent').html('');
    $.post('/snafu/configuration/host/'+pk+'/del',{ csrfmiddlewaretoken:$('input[name="csrfmiddlewaretoken"]').val() }, function(data) {
      $('#glpihostTab').html(data)
      $('#host'+pk+'Tab').hide('300');
    })
  }

//////////////////////////////////////////////////

  // GET A GLPI CATEGORY
  $.fn.getCategory = function(pk){
    $('#categoryContent').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/category/'+pk+'/get', function(data) {
      $('#categoryContent').html(data);
    })
  }

  // MY CAT FILTER
  $.fn.getCategories = function(){
    $('#categoryContent').html();
    $('#Ca_tbody').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/category_q',{'q': $('#cat_q').val() }, function(data) {
      $('#Ca_tbody').html( data );
    });
  }

 // GOTO ADDCAT
  $.fn.getCategoryForm = function(){
    $.get('/snafu/configuration/category/form', {}, function(data) {
      $('#addCategoryContent').html(data)
      $('#addCategoryTab').tab('show')
    })
  }

 // ADD A CAT FROM FORM
  $.fn.addCategory = function(){
    $('#categoryContent').html('');

    if ( ! $('#categoryForm input[name="id"]').val() ) { var cat_id = 0; }
    else { var cat_id = $('#hostForm input[name="id"]').val(); };

    $.ajax({ 
      type: "POST", 
      url: '/snafu/configuration/category/'+cat_id+'/add', 
      data: $('#categoryForm').serialize(),
      async: false,
      cache: false,
      success: function(data) {
         $('#categoryTab').html(data);
         $('#CategoryListTab').tab('show');
      },
      error: function() { alert('err'); }
    })
  }

  $('#categoryForm').submit(function() {
    $.fn.addCategory();
    return false;
  });

 // DEL CAT
  $.fn.delCategory = function(pk){
    $('#CategoryContent').html('');
    $.post('/snafu/configuration/category/'+pk+'/del',{ csrfmiddlewaretoken:$('input[name="csrfmiddlewaretoken"]').val() }, function(data) {
      $('#categoryTab').html(data)
      $('#cat'+pk+'Tab').hide('300');
    })
  }


//////////////////////////////////////////////////
 // ASK QUESTION BEFORE LAUNCH FUNCTION
  $.fn.Question = function(question, func){
    $('#infoModal').modal('hide');
    $('#infoModal').html(question, func);
  }

//////////////////////////////////////////////////
  $.fn.getHostDiff = function(){
    $('#hostDiff').html('<img id="loader" src="/static/img/ajax-loader.gif" height="100%" width="100%">' );
    $.get('/snafu/configuration/host/diff',{}, function(data) {
      $('#hostDiff').html(data);
    });
  }

});

