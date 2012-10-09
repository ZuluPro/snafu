$(document).ready(function() {

  $('button[num]').live( 'click', function(){
    $.fn.validRef($(this).attr('num'));
    return false
  });

  $.fn.validRef = function(refId){

    var R = { treatment_q:true, eventPk:$('input[name=eventPk]').val() };
    var form = $('#R'+refId+'Form')
    var refTabContent = $('#R'+refId+'TabContent')

    $('div[class*="active"] input').each(function(index) {
      R[$(this).attr('name')] = $(this).val();
    });
    $('div[class*="active"] select').each(function(index) {
      R[$(this).attr('name')] = $(this).val();
    });

    refTabContent.html('<img id="loader" src="/static/img/ajax-loader.gif">');
    $.ajax({ 
      type: "POST", 
      url: "/snafu/configuration", 
      data: R,
      async: true,
      cache: false,
      error: function() { alert('err'); },
      success: function(data){
    //    form.hide(500);
        refTabContent.hide(500);
      }
    });
    if ( $('form:not([style*="display: none"])').length == 0 ) { 
      $('#submit').submit();
    } else {
      $('#alertTab a:not([style*="display: none"])').tab('show');
    } ;
  }

});
