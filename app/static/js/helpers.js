// Show/Hide EUR Preview jQuery
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

// enable bootstrap tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})
