// Show/Hide EUR Preview jQuery
// TODO add all jQuery related/AJAX/JS in here or relevant JS files
$(document).ready(function(){
  $('button[name="show_eurview"]').click(function(){
    $('tr[class="table-primary eurview"]').show();
    $('tr[class="table-primary eurview"]').show();
    $('button[name="hide_eurview"]').show();
  });
  $('button[name="hide_eurview"]').click(function(){
    $('tr[class="table-primary eurview"]').hide()
    $('tr[class="table-primary eurview"]').hide()
    $('button[name="hide_eurview"]').hide();

  });
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})
