var VIDEO_ID;
var CSRFTOKEN;
var TAGGED_COMMENTS = {};
var SUSPICIOUS_SPAM = [];
var SUSPICIOUS_HAM = [];
var NEXT_URL;

var TAG = '<div class="small-3 columns">' +
          '<span class="comment_tag right tiny secondary button spam" tag="spam">Spam</span>' +
          '<span class="comment_tag right tiny secondary button ham" tag="ham">Ham</span>' +
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
      NEXT_URL == null) {
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
    $('#comments').append(formattedComment(
      newComment.comment_id, newComment.author, newComment.date,
      newComment.content, TAG, 'unclassified'));
  }
}

$(document).ready(function(){
  /* Initializing some global variables */
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video-title').attr('video-id');

  $('#comments').children('.comment-row[tag-type=manual]').each(function() {
    TAGGED_COMMENTS[$(this).attr('comment-id')] = $(this).attr('comment-id');
  });

  NEXT_URL = 'https://gdata.youtube.com/feeds/api/videos/'+ VIDEO_ID +
             '/comments?alt=json&max-results=50&orderby=published';

  //getNewComments(nextHandler, total_length, spam_length, ham_length)
  getNewComments(putNewComments, 1000, 20, 30);

  /* EVENTS */
  $('.comments-section').on('click', '.comment_tag', function() {
    saveComment($(this), function() {
      if (parseInt($spamCount.attr('value')) >= 10 && parseInt($hamCount.attr('value')) >= 10) {
        $('#classify-button').removeAttr('disabled');
      } else {
        $('#classify-button').attr('disabled', true);
      }
    });
    return false;
  });

  $more_comments.click(function() {
    if (!$more_comments.attr('disabled')) {
      console.log('More comments...');

      if (NEXT_URL != null) {
        $more_comments.html('Loading ...');
        lockLoadingButton($more_comments);
        getNewComments(putNewComments, 1000, 20, 30);
      } else {
        putNewComments();
      }
    }

    return false;
  });

  $('#classify-button').click(function(event) {
    if ($(this).attr('disabled')) {
      event.preventDefault();
    }
  });

  $('#hide-spam-button').click(function(event) {
    if ($(this).attr('action') == 'hide') {
      $('#comments').find('.comment_tag[tag=spam][disabled]').parent().parent().fadeOut(1);
      $(this).attr('action', 'show');
      $(this).html('Show spam');
    } else {
      $('#comments').find('.comment_tag[tag=spam][disabled]').parent().parent().fadeIn(1);
      $(this).attr('action', 'hide');
      $(this).html('Hide spam');
    }
  });
});
