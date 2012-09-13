$(document).ready(function() {

  $('button[num]').live( 'click', function(){
    $.fn.validRef($(this).attr('num'));
    return false
  });

  $.fn.validRef = function(refId){

    var R = {}
    var form = $('#R'+refId+'Form')
    var tab = $('#R'+refId+'Tab')

    $('form input').each(function(index) {
      R[$(this).attr('name')] = $(this).val();
    });
    $('form select').each(function(index) {
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
