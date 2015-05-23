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

var $moreComments = $('#moreComments');
var $classifiedCount = $('.classifiedCount');
var $spamCount = $('#spamCount');
var $hamCount = $('#hamCount');

function lockMoreCommentsButton() {
  $moreComments.html('Loading ...');
  $moreComments.addClass('loading-icon');
  $moreComments.attr('disabled', true);
}
function unlockMoreCommentsButton() {
  $moreComments.html('Show more comments <i class="fi-refresh"></i>');
  $moreComments.removeClass('loading-icon');
  $moreComments.removeAttr('disabled');
}

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
    $moreComments.remove();
  } else {
    unlockMoreCommentsButton();
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

function suspiciousComment(content) {
  var fixed = content.replace(/ /g,'').toLowerCase();

  if (fixed.indexOf('visit') != -1 || fixed.indexOf('.co') != -1 ||
      fixed.indexOf('http') != -1 || fixed.indexOf('buy') != -1 ||
      fixed.indexOf('check') != -1 || fixed.indexOf('channel') != -1 ||
      fixed.indexOf('site') != -1 || fixed.indexOf('subscrib') != -1) {
    return true;
  }
  return false;
}

function saveComment(saveButton) {
  var $root = saveButton.parent().parent();

  var comment_id = $root.attr('comment-id');
  var tag = saveButton.attr('tag');
  var content = $root.find('.comment_content').html();
  var author = $root.find('.comment_author').html();
  var date = $root.find('.comment_date').html();

  $.ajax({
    type: 'POST',
    url: saveComment_ajax_url,
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: {comment_id: comment_id,
        video_id: VIDEO_ID,
        author: author,
        date: date,
        content: content,
        tag: tag },
    dataType: 'text'
  }).fail(function(data) {
    console.log(data.responseText);

  }).done(function(num_untrd_comments) {
    var sibling = saveButton.siblings();

    if (tag == 'spam') {
      incrementCounter($spamCount);
      if ($root.attr('tag-type') == 'manual') {
        decrementCounter($hamCount);
      } else {
        incrementCounter($classifiedCount);
      }
      saveButton.addClass('alert');
      sibling.removeClass('success');

    } else {
      incrementCounter($hamCount);
      if ($root.attr('tag-type') == 'manual') {
        decrementCounter($spamCount);
      } else {
        incrementCounter($classifiedCount);
      }
      saveButton.addClass('success');
      sibling.removeClass('alert');
    }

    saveButton.attr('disabled', true);
    sibling.removeAttr('disabled');
    $root.attr('tag-type', 'manual');

    if (parseInt($spamCount.attr('value')) >= 10 && parseInt($hamCount.attr('value')) >= 10) {
      $('#classify-button').removeAttr('disabled');
    } else {
      $('#classify-button').attr('disabled', true);
    }

    console.log(num_untrd_comments);
  });
}

$(document).ready(function(){
  /* Initializing some global variables */
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video-title').attr('video-id');

  $('#comments').children('.comment[tag-type=manual]').each(function() {
    TAGGED_COMMENTS[$(this).attr('comment-id')] = $(this).attr('comment-id');
  });

  NEXT_URL = 'https://gdata.youtube.com/feeds/api/videos/'+ VIDEO_ID +
             '/comments?alt=json&max-results=50&orderby=published';

  //getNewComments(nextHandler, total_length, spam_length, ham_length)
  getNewComments(putNewComments, 1000, 20, 30);

  /* EVENTS */
  $('#comments').on('click', '.comment_tag', function() {
    var $this = $(this);
    if (!$this.attr('disabled')) {
      saveComment($this);
    }
    return false;
  });

  $('#moreComments').click(function() {
    if (!$(this).attr('disabled')) {
      console.log('More comments...');

      if (NEXT_URL != null) {
        lockMoreCommentsButton();
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
