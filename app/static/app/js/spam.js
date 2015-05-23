var VIDEO_ID;
var CSRFTOKEN;
var CLASSIFIED_COMMENTS = {};
var NEXT_PAGE_TOKEN;

var BUTTON = 'comment_tag right tiny secondary button';
var SPAM_TAG = '<div class="tag_column small-3 columns">' +
          '<span class="'+ BUTTON +' alert spam" disabled tag="spam">Spam</span>' +
          '<span class="'+ BUTTON +' ham" tag="ham">Ham</span>' +
          '</div>';

var $moreComments = $('#more-comments');
var $classifiedCount = $('.classifiedCount');
var $spamCount = $('#spamCount');
var $hamCount = $('#hamCount');

function lockLoadingButton($loadingButton) {
  $loadingButton.addClass('loading-icon');
  $loadingButton.attr('disabled', true);
}
function unlockLoadingButton($loadingButton) {
  $loadingButton.removeClass('loading-icon');
  $loadingButton.removeAttr('disabled');
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
    $('#new-comments').append(formattedComment(
      newComment.comment_id, newComment.author, newComment.date,
      newComment.content, TAG, 'unclassified'));
  }
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

function predictSpam() {
  $.ajax({
    type: 'GET',
    url: predictSpam_ajax_url,
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: { v: VIDEO_ID, next_page_token: NEXT_PAGE_TOKEN },
    dataType: 'json'
  }).fail(function(data) {
    $moreComments.remove();
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
    //   $moreComments.remove();
    // } else {
      $moreComments.html('Show more comments <i class="fi-refresh"></i>');
      unlockLoadingButton($moreComments);
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
  $('.comments').on('click', '.comment_tag', function() {
    var $this = $(this);
    if (!$this.attr('disabled')) {
      saveComment($this);
    }
    return false;
  });

  $('#more-comments').click(function() {
    if (!$(this).attr('disabled')) {
      console.log('More comments...');

      if (NEXT_PAGE_TOKEN != null) {
        lockMoreCommentsButton();
        getNewComments(putNewComments, 1000, 20, 30);
      } else {
        putNewComments();
      }
    }

    return false;
  });
});
