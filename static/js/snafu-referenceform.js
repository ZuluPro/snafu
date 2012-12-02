$(document).ready(function() {

  $('button[id="addRefBtn"]').each(function(index) {
     $(this).hide();
  });

  $('button[num]').live( 'click', function(){
    $.fn.validRef($(this).attr('num'));
    return false
  });

  $.fn.validRef = function(refId){

    var R = { treatment_q:true, eventPk:$('input[name=eventPk]').val() };
    var refTab = $('#R'+refId+'Tab');
    var refTabContent = $('#R'+refId+'TabContent');

    $('div[class*="active"] input').each(function(index) {
      R[$(this).attr('name')] = $(this).val();
    });
    $('div[class*="active"] select').each(function(index) {
      R[$(this).attr('name')] = $(this).val();
    });

    $.ajax({ 
      type: "POST", 
      url: "/snafu/event/addref", 
      data: R,
      async: false,
      cache: false,
      error: function() { alert('err'); },
      success: function(data,status,xhr){
        var ct = xhr.getResponseHeader("content-type") || "";

        if (ct.indexOf('html') > -1) {
          refTabContent.html('<img id="loader" src="/static/img/ajax-loader.gif">');
          refTab.hide(250);
          refTab.attr('class','hidden');
          refTabContent.hide(500);
          $('li:not([class*=active]) a[data-toggle=tab]:not([class*=hidden]):first').tab('show');
    if ( $('form').length == 1 ) { 
      $('#submit').submit();
    }
        } else if (ct.indexOf('json') > -1) {
          var errors = JSON.parse(xhr.responseText);
          $('.tabbable').prepend('<div id="msg-info" class="alert alert-error" style="display: block;"><h4>Erreur(s) de formulaire :</h4><p class="pull-right"><button class="close" onclick="$(\'#msg-info\').hide(250); return false;">×</button></p><ul id="msg-content"></ul></div>');
          for ( var k in errors) {
            $('#msg-content').prepend('<li><b>'+k+'</b> : '+errors[k]+'</li>');
          }
        }  
      }
    });
     
  }

$('form').submit(function(){
    $(':submit', this).click(function() {
        return false;
    });
});
});
