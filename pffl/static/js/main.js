jQuery(function($) {
  $(document).ready(function() {

    /* -------------------------------- *
     * Define smoothstate.js behavior
     * -------------------------------- */
    $(function() {
      'use strict';
      var $page = $('#main'),
        options = {
          debug: true,
          prefetch: true,
          cacheLength: 0,
          blacklist: '.no-smoothState',
          onBefore: function($currentTarget, $container) {
          },
          onStart: {
            duration: 350,
            render: function($container) {
                $container.addClass('is-exiting');
                smoothState.restartCSSAnimations();
            }
          },
          onReady: {
            duration: 0,
            render: function($container, $newContent) {
                $container.removeClass('is-exiting');
                $container.html($newContent);
            }
          }
        },
        smoothState = $page.smoothState(options).data('smoothState');
    });
  });


  if($('select[name=theme] option:selected').val()=="light") {
    $('body').removeClass('dark');
  }
  else if($('select[name=theme] option:selected').val()=="dark") {
    $('body').addClass('dark');
  }
  else if($('select[name=theme] option:selected').val()=="both") {
    var d = new Date();
    var h = d.getHours();
    if(h<=9 || h>=5)
      $('body').addClass('dark');
    else 
      $('body').removeClass('dark');
  }
});

var fast = 250;
var normal = 500;

$('.toggleLink').on('click', function() {
  var showItems = $(this).attr('toggleShow').split(' ');
  var hideItems = $(this).attr('toggleHide').split(' ');
  var data = $(this).attr('toggleData');
  var delay = $(this).attr('toggleDelay');
  if(delay) {
    setTimeout(function() {
      for(var i=0; i<hideItems.length; i++)
        $('#'+hideItems[i]).fadeOut(fast);
      setTimeout(function() {
        for(var i=0; i<showItems.length; i++) {
          $('#'+showItems[i]).fadeIn(fast);
          if(data)
            $('#'+showItems[i]).attr('toggleData', data);
        }
      }, fast);
    }, parseInt(delay));
    return;
  }

  for(var i=0; i<hideItems.length; i++)
    $('#'+hideItems[i]).fadeOut(fast);
  setTimeout(function() {
    for(var i=0; i<showItems.length; i++) {
      $('#'+showItems[i]).fadeIn(fast);
      if(data)
        $('#'+showItems[i]).attr('toggleData', data);
    }
  }, fast);
});