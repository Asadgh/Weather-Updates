$(document).ready(function() {
    // Handle the form submission
    $('#weather-form').submit(function(event) {
      // Prevent the form from submitting if the validation fails
      if ($('#cur_nest').val() === 'select' && $('#launcher').val() === 'select') {
        alert('Please Select A Valid Nest and Launcher Direction');
        event.preventDefault();
      }
      else if ($('#cur_nest').val() === 'select') {
        alert('Please Select A Valid Nest');
        event.preventDefault();
      }
      else if ($('#launcher').val() === 'select') {
        alert('Please Select A Valid Launcher Direction');
        event.preventDefault();
      }
    });
  });

function dismissCookieBanner() {
    document.querySelector('.cookie-banner').style.display = 'none';
}
