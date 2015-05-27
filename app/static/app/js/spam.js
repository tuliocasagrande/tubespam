var VIDEO_ID;
var CSRFTOKEN;
var CLASSIFIED_COMMENTS = {};
var NEXT_PAGE_TOKEN;

var BUTTON = 'comment_tag right tiny secondary button';
var SPAM_TAG = '<div class="tag_column small-3 columns">' +
          '<span class="'+ BUTTON +' alert spam" disabled tag="spam">Spam</span>' +
          '<span class="'+ BUTTON +' ham" tag="ham">Ham</span>' +
          '</div>';

var $classifiedCount = $('.classifiedCount');
var $spamCount = $('#spamCount');
var $hamCount = $('#hamCount');

function incrementCounter($counter) {
  var newValue = parseInt($counter.attr('value')) +1;
  $counter.attr('value', newValue);
  $counter.html(formattedNumber(newValue));
}
function decrementCounter($counter) {
  var newValue = parseInt($counter.attr('value')) -1;
  $counter.attr('value', newValue);
  $counter.html(formattedNumber(newValue));
}

function putNewComments() {
  appendToHtml(SUSPICIOUS_SPAM, 20);
  appendToHtml(SUSPICIOUS_HAM, 30);

  if (SUSPICIOUS_SPAM.length == 0 && SUSPICIOUS_HAM.length == 0 &&
      NEXT_PAGE_TOKEN == null) {
    $more_comments.remove();
  } else {
    $more_comments.html('Show more comments <i class="fi-refresh"></i>');
    unlockLoadingButton($more_comments);
  }
}

function appendToHtml(list, count) {
  var newComment;
  var len = list.length < count ? list.length : count;

  for (var i = 0; i < len; i++) {
    newComment = list.shift();
    $('#new-comments').append(formattedComment(
      newComment.comment_id, newComment.author, newComment.date,
      newComment.content, TAG, 'unclassified'));
  }
}

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
    for (var key in data) {
      $('#new-comments').append(formattedComment(
                            key, data[key].author, data[key].date,
                            data[key].content, SPAM_TAG, 'automatic'));
    }

    // if (SUSPICIOUS_SPAM.length == 0 && SUSPICIOUS_HAM.length == 0 &&
    //   NEXT_URL == null) {
    //   $more_comments.remove();
    // } else {
      $more_comments.html('Show more comments <i class="fi-refresh"></i>');
      unlockLoadingButton($more_comments);
      $('#export-modal-button').removeAttr('disabled');
    // }
  });
}

$(document).ready(function(){
  /* Initializing some global variables */
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video-title').attr('video-id');

  $('#classified-comments').children('.comment-row[tag-type=manual]').each(function() {
    CLASSIFIED_COMMENTS[$(this).attr('comment-id')] = $(this).attr('comment-id');
  });

  //getNewComments(nextHandler, total_length, spam_length, ham_length)
  //getNewComments(putNewComments, 1000, 20, 30);
  NEXT_PAGE_TOKEN = 'None'
  predictSpam();

  /* EVENTS */
  $('.comments-section').on('click', '.comment_tag', function() {
    saveComment($(this));
    return false;
  });

  $more_comments.click(function() {
    // if (!$more_comments.attr('disabled')) {
    //   console.log('More comments...');

    //   if (NEXT_PAGE_TOKEN != null) {
    //     $more_comments.html('Loading ...');
    //     lockLoadingButton($more_comments);
    //     //getNewComments(putNewComments, 1000, 20, 30);
    //   } else {
    //     putNewComments();
    //   }
    // }
    // TODO: predictSpam call
    return false;
  });
});
