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

    refTabContent.html('<img id="loader" src="/static/img/ajax-loader.gif">');
    $.ajax({ 
      type: "POST", 
      url: "/snafu/event/addref", 
      data: R,
      async: false,
      cache: false,
      error: function() { alert('err'); },
      success: function(data){
        refTab.hide(250);
        refTab.attr('class','hidden');
        refTabContent.hide(500);
        $('li:not([class*=active]) a[data-toggle=tab]:not([class*=hidden]):first').tab('show')
      }
    });
    if ( $('form').length == 1 ) { 
      $('#submit').submit();
    }// else {
     
   // } ;
  }

});
