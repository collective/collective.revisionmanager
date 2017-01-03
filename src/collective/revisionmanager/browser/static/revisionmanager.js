$(document).ready(function () {
  $('#checkAll').click(function(e){
    e.preventDefault();
    $('input[type="checkbox"][name="delete:list"]').click();
  });
})
