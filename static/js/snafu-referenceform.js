$(document).ready(function() {

  $('button[num]').live( 'click', function(){
    $.fn.validRef($(this).attr('num'));
    return false
  });

  $.fn.validRef = function(refId){

    var R = { treatment_q:true, eventPk:$('input[name=eventPk]').val() };
    var form = $('#R'+refId+'Form')
    var tab = $('#R'+refId+'Tab')

    $('div[class*="active"] input').each(function(index) {
      R[$(this).attr('name')] = $(this).val();
    });
    $('div[class*="active"] select').each(function(index) {
      R[$(this).attr('name')] = $(this).val();
    });

    $.ajax({ 
      type: "POST", 
      url: "/events/configuration", 
      data: R,
      async: false,
      cache: false,
      error: function() { alert('err'); },
      success: function(data){
        form.hide(500);
        tab.hide(500);
      }
    });
    if ( $('form:not([style*="display: none"])').length == 1 ) { 
      $('#submit').submit();
    } else {
      $('#alertTab a:not([style*="display: none"])').tab('show');
    } ;
  }

});
