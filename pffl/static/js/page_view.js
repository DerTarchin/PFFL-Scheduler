var csrf = $("#csrf").val();

$('#export').on('click', function() {
  var $export_button = $(this);
  var export_url = $export_button.attr('url');
  $export_button.css('opacity',.3);
  $export_button.css('cursor',"default");

  send_data = {
      csrfmiddlewaretoken: csrf
  };

  $.ajax({
    url: export_url,   
    data: send_data,
    type: "POST",
    dataType : "json",
    success: function(json) {
      if (!json.error) {
        alert("Your schedule has been exported: visit your Google account to view it.");
        $export_button.css('opacity',1);
        $export_button.css('cursor',"");
      }
      else {
      	alert(json.message);
      }
    },
    error: function(xhr, status, errorThrown) {
        alert("Error: " + errorThrown);
    },
    complete: function( xhr, status ) {
      return;
    }
  });
});