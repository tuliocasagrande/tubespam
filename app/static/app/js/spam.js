function predictSpam() {
  $.ajax({
    type: 'GET',
    url: predictSpam_ajax_url,
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: { v: VIDEO_ID, next_page_token: NEXT_PAGE_TOKEN },
    dataType: 'json'
  }).fail(function(data) {
    $more_comments.remove();
    console.log('ERROR! The server did\'t return a correct JSON.');
    console.log(data.responseText);
    console.log(data);
  }).done(function(data) {
    NEXT_PAGE_TOKEN = data['next_page_token'];
    for (var key in data['comments']) {
      var c = data['comments'][key];
      $('#predicted-comments').append(formattedComment(key, c.author, c.date,
                                      c.content, SPAM_TAG, 'automatic'));
    }

    if (NEXT_PAGE_TOKEN == 'None') {
      $more_comments.remove();
    } else {
      unlockLoadingButton($more_comments, 'Show more comments <i class="fi-refresh"></i>');
      $('#export-modal-button').removeAttr('disabled');
    }
  });
}

$(document).ready(function(){
  /* Initializing some global variables */
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video-title').attr('video-id');
  NEXT_PAGE_TOKEN = 'None'

  /* Events listeners */
  $('.comments-section').on('click', '.comment_tag', function() {
    saveComment($(this));
    return false;
  });

  $more_comments.click(function() {
    lockLoadingButton($more_comments, 'Loading ...');
    predictSpam();
    return false;
  });

  /* Main function first call */
  predictSpam();
});
