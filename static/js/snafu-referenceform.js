  function validRef(refId){

   var R = {}
   var form = $('#R'+refId+'Form')
   var tab = $('#R'+refId+'Tab')

   $('form input').each(function(index) {
     R[$(this).attr('name')] = $(this).val();
   });
   $('form select').each(function(index) {
     R[$(this).attr('name')] = $(this).val();
   });

   $.post('events/configuration',R, function(data) {} )
    .error(function() { alert("error"); })
    .complete(function() {
   if ( $('form:not([style*="display: none"])').size() == 1 ) {
   form.hide();
   tab.hide();
   $('#submit').submit();
  //  window.location.replace("/events");
   } else {
   form.hide();
   tab.hide();
    }
   })
  }

