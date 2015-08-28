var VIDEO_ID;
var CSRFTOKEN;
var TAGGED_COMMENTS = {};
var SUSPICIOUS_SPAM = [];
var SUSPICIOUS_HAM = [];
var NEXT_URL;

function sendToClassifier() {
  var comments = mergeLists(SUSPICIOUS_SPAM, 40, SUSPICIOUS_HAM, 60);

  $.ajax({
    type: 'POST',
    url: train_ajax_url,
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: { v: VIDEO_ID, 'comments[]': comments },
    dataType: 'json'
  }).fail(function(data) {
    $more_comments.remove();
    console.log('ERROR! The server did\'t return a correct JSON.');
    console.log(data.responseText);

  }).done(function(data) {

    for (var key in data) {
      if (data[key].tag === "1") {
        $('#comments').append(formattedComment(
                              key, data[key].author, data[key].date,
                              data[key].content, SPAM_TAG, 'automatic'));
      } else {
        $('#comments').append(formattedComment(
                              key, data[key].author, data[key].date,
                              data[key].content, HAM_TAG, 'automatic'));
      }
    }

    if (SUSPICIOUS_SPAM.length == 0 && SUSPICIOUS_HAM.length == 0 &&
      NEXT_URL == null) {
      $more_comments.remove();
    } else {
      unlockLoadingButton($more_comments, 'Show more comments <i class="fi-refresh"></i>');
      $('#export-modal-button').removeAttr('disabled');
    }
  });
}

function retrainClassifier() {
  var $comments = $('#comments');
  var $classified_comments = $('#classified-comments');

  var $commentsChildrenManual = $comments.children('.comment-row[tag-type=manual]');
  $commentsChildrenManual.each(function() {
    $classified_comments.append('<hr/>')
    $(this).appendTo($classified_comments);
  });

  var newList = [];
  var $commentsChildrenAutomatic = $comments.children('.comment-row[tag-type=automatic]');
  $commentsChildrenAutomatic.each(function() {
    newComment = {comment_id: $(this).attr('comment-id'),
                  author: $(this).find('.comment_author').html(),
                  date: $(this).find('.comment_date').html(),
                  content: $(this).find('.comment_content').html()};
    $(this).remove();
    newList.push(JSON.stringify(newComment));
  });

  $comments.html('<h3>Prediction</h3><hr/>');

  $.ajax({
    type: 'POST',
    url: train_ajax_url,
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: { v: VIDEO_ID, 'comments[]': newList },
    dataType: 'json'
  }).done(function(data) {

    for (var key in data) {
      if (data[key].tag === "1") {
        $('#comments').append(formattedComment(
                              key, data[key].author, data[key].date,
                              data[key].content, SPAM_TAG, 'automatic'));
      } else {
        $('#comments').append(formattedComment(
                              key, data[key].author, data[key].date,
                              data[key].content, HAM_TAG, 'automatic'));
      }
    }
  });
}

function mergeLists(spam_list, spam_length, ham_list, ham_length) {
  var newList = [];
  var newComment;

  var len = spam_list.length < spam_length ? spam_list.length : spam_length;
  for (var i = 0; i < len; i++) {
    newComment = spam_list.shift();
    newList.push(JSON.stringify(newComment));
  }

  len = ham_list.length < ham_length ? ham_list.length : ham_length;
  for (var i = 0; i < len; i++) {
    newComment = ham_list.shift();
    newList.push(JSON.stringify(newComment));
  }

  return newList;
}

function exportComments() {
  $('#export-button').prop('disabled', false);
  $('#export-form').submit();
}

$(document).ready(function(){
  /* Initializing some global variables */
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video-title').attr('video-id');

  $('#classified-comments').children('.comment-row[tag-type=manual]').each(function() {
    TAGGED_COMMENTS[$(this).attr('comment-id')] = $(this).attr('comment-id');
  });

  NEXT_URL = 'https://gdata.youtube.com/feeds/api/videos/'+ VIDEO_ID +
             '/comments?alt=json&max-results=50&orderby=published';

  //getNewComments(nextHandler, total_length, spam_length, ham_length)
  getNewComments(sendToClassifier, 500, 40, 60);

  /* EVENTS */
  $('.comments-section').on('click', '.comment_tag', function() {
    saveComment($(this), function(num_untrd_comments) {
      if (num_untrd_comments >= 5) {
        refit = confirm(num_untrd_comments +' comments were manually fixed since the last training. Retrain the classifier?')
        if (refit) retrainClassifier();
      }
    });
    return false;
  });

  $more_comments.click(function() {
    if (!$more_comments.attr('disabled')) {
      console.log('More comments...');

      if (NEXT_URL != null) {
        lockLoadingButton($more_comments, 'Loading ...');
        getNewComments(sendToClassifier, 500, 40, 60);
      } else {
        sendToClassifier();
      }
    }

    return false;
  });

  $('input[name=export-option]').change(function() {
    var exportOption = $('input[name=export-option]:checked', '#export-form').val();
    if (exportOption === 'm') {
      $('.ext-options-text').addClass('disabled');
      $('.ext-options').attr('disabled', true);
    } else {
      $('.ext-options-text').removeClass('disabled');
      $('.ext-options').removeAttr('disabled');
    }
  });

  $('#export-form').submit(function() {
    var $export_button = $('#export-button');
    if ($export_button.attr('disabled')) {
      return false;
    }

    lockLoadingButton($export_button);
    var $export_comments = $('#export-comments');
    $export_comments.empty();

    /* Export options:
     * m  => manually classified only
     * mu => manually classified and unclassified
     */
    var exportOption = $('input[name=export-option]:checked', '#export-form').val();
    if (exportOption !== 'm') {

      var exportAmount = $('#export-amount').val();
      if (exportAmount <= 0) exportAmount = 0;

      var $commentsChildrenAutomatic = $('#comments').children('.comment-row[tag-type=automatic]');
      var newComment;
      var spam_length, ham_length;
      spam_length = ham_length = exportAmount;

      /* If there is not enough unclassified comments, fetching new comments */
      if (($commentsChildrenAutomatic.length + SUSPICIOUS_SPAM.length + SUSPICIOUS_HAM.length < exportAmount) &&
          (NEXT_URL != null)) {
        getNewComments(exportComments, exportAmount, spam_length, ham_length);
        return false;
      }

      /* Handling comments already displayed */
      $commentsChildrenAutomatic.each(function() {

        newComment = {comment_id: $(this).attr('comment-id'),
                      author: $(this).find('.comment_author').html(),
                      date: $(this).find('.comment_date').html(),
                      content: $(this).find('.comment_content').html()};

        newComment = JSON.stringify(newComment).replace(/"/g, '&quot;');
        $export_comments.append('<input type="hidden" name="comments" value="'+newComment+'">');
      });

      /* Handling hidden comments */
      var len = SUSPICIOUS_SPAM.length < spam_length ? SUSPICIOUS_SPAM.length : spam_length;
      for (var i = 0; i < len; i++) {
        newComment = SUSPICIOUS_SPAM[i];
        newComment = JSON.stringify(newComment).replace(/"/g, '&quot;');
        $export_comments.append('<input type="hidden" name="comments" value="'+newComment+'">');
      }

      len = SUSPICIOUS_HAM.length < ham_length ? SUSPICIOUS_HAM.length : ham_length;
      for (var i = 0; i < len; i++) {
        newComment = SUSPICIOUS_HAM[i];
        newComment = JSON.stringify(newComment).replace(/"/g, '&quot;');
        $export_comments.append('<input type="hidden" name="comments" value="'+newComment+'">');
      }
    }
    unlockLoadingButton($export_button);
    $('#export-modal').foundation('reveal', 'close');
  });

});
