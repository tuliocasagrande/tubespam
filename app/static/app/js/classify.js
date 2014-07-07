var VIDEO_ID;
var CSRFTOKEN;
var TAGGED_COMMENTS = {};
var SUSPICIOUS_SPAM = [];
var SUSPICIOUS_HAM = [];
var NEXT_URL;

var BUTTON = 'comment_tag right tiny secondary button';
var TAG = '<div class="small-3 columns">' +
          '<span class="'+ BUTTON +' spam" tag="spam">Spam</span>' +
          '<span class="'+ BUTTON +' ham" tag="ham">Ham</span>' +
          '</div>';

var SPAM_TAG = '<div class="small-3 columns">' +
          '<span class="'+ BUTTON +' alert spam" disabled tag="spam">Spam</span>' +
          '<span class="'+ BUTTON +' ham" tag="ham">Ham</span>' +
          '</div>';

var HAM_TAG = '<div class="small-3 columns">' +
          '<span class="'+ BUTTON +' spam" tag="spam">Spam</span>' +
          '<span class="'+ BUTTON +' success ham" disabled tag="ham">Ham</span>' +
          '</div>';

var $moreComments = $('#moreComments');
var $taggedCount = $('#taggedCount');
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

function formattedComment(id, content, tag, tagType) {
  tagType = typeof tagType !== 'undefined' ? tagType : '';

  var comment = '<div class="comment row" tagType="'+ tagType +'" comment_id="'+ id +'">' +
                '<p class="comment_content small-9 columns">'+ content +'</p>' +
                tag +'</div><hr/>';

  return comment;
}

function formattedDate(date) {
  var MONTH_NAMES = ["Jan ", "Feb ", "Mar ", "Apr ", "May ", "Jun ",
                     "Jul ", "Aug ", "Sep ", "Oct ", "Nov ", "Dec "];

  return 'Uploaded on ' + MONTH_NAMES[date.getMonth()] + date.getDate() + ', ' + date.getFullYear();
}

function formattedNumber(number, decimals, dec_point, thousands_sep) {
  // http://kevin.vanzonneveld.net
  // +   original by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
  // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +   bugfix by: Michael White (http://crestidg.com)
  // +   bugfix by: Benjamin Lupton
  // +   bugfix by: Allan Jensen (http://www.winternet.no)
  // +  revised by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
  // *   example 1: number_format(1234.5678, 2, '.', '');
  // *   returns 1: 1234.57

  var n = number, c = isNaN(decimals = Math.abs(decimals)) ? 0 : decimals;
  var d = dec_point == undefined ? "." : dec_point;
  var t = thousands_sep == undefined ? "," : thousands_sep, s = n < 0 ? "-" : "";
  var i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;

  return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
}

function getVideoMeta(video_id) {
  var url = 'https://gdata.youtube.com/feeds/api/videos/'+ video_id +'?alt=json';
  $.ajax({
    type: 'GET',
    url: url,
    dataType: 'json'
  }).done(function(data){
    document.title = data.entry.title.$t;
    $('#video_title').html(data.entry.title.$t);
    $('#video_publish_date').html(formattedDate(new Date(data.entry.published.$t)));
    $('#video_content').html(data.entry.content.$t);

    $('#viewCount').html(formattedNumber(data.entry.yt$statistics.viewCount));

    try {
      var commentCount = data.entry.gd$comments.gd$feedLink.countHint;
      $('#commentCount').html(formattedNumber(commentCount));
    } catch(e) {
      $('#comments').append("Comments are disabled for this video.");
      $moreComments.remove();
    }
  });
}

function getNewComments(nextHandler, total_length, spam_length, ham_length) {

  if (!nextHandler || (typeof nextHandler !== "function")) {
    console.log('error: callback is not a function');
    console.log(nextHandler);
  }

  $.ajax({
    type: 'GET',
    url: NEXT_URL,
    dataType: 'json'
  }).fail(function() {
    $('#comments').append("Comments are disabled for this video.");
    $moreComments.remove();
  }).done(function(data){
    loadNewComments(data);
    console.log(SUSPICIOUS_SPAM.length + SUSPICIOUS_HAM.length);

    if (data.feed.link[data.feed.link.length-1].rel == 'next') {
      NEXT_URL = data.feed.link[data.feed.link.length-1].href;
    } else {
      NEXT_URL = null;
      nextHandler();
      return;
    }

    if ((SUSPICIOUS_SPAM.length + SUSPICIOUS_HAM.length > total_length) ||
        (SUSPICIOUS_SPAM.length > spam_length && SUSPICIOUS_HAM.length > ham_length)) {
      nextHandler();
      return;
    }

    getNewComments(nextHandler, total_length, spam_length, ham_length);
  });
}


function loadNewComments(data) {
  var comment_id, start_index, content, newComment;

  for (var i = 0, len = data.feed.entry.length; i < len; i++) {
    start_index = data.feed.entry[i].id.$t.lastIndexOf('/') + 1;
    comment_id = data.feed.entry[i].id.$t.substring(start_index);
    content = data.feed.entry[i].content.$t;

    if (TAGGED_COMMENTS.hasOwnProperty(comment_id)) {
      continue;
    } else if (!content.trim()) {
      continue;
    }

    newComment = {comment_id: comment_id, content: content};
    if (suspiciousComment(content)) {
      SUSPICIOUS_SPAM.push(newComment);
    } else {
      SUSPICIOUS_HAM.push(newComment);
    }
  }
}

function sendToClassifier() {
  var comments = mergeLists(SUSPICIOUS_SPAM, 40, SUSPICIOUS_HAM, 60);

  $.ajax({
    type: 'POST',
    url: '/train',
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: { v: VIDEO_ID, 'comments[]': comments },
    dataType: 'json'
  }).done(function(data) {

    for (var key in data) {
      if (data[key].tag === "1") {
        $('#comments').append(formattedComment(key,
          data[key].content, SPAM_TAG, 'automatic'));
      } else {
        $('#comments').append(formattedComment(key,
          data[key].content, HAM_TAG, 'automatic'));
      }
    }

    if (SUSPICIOUS_SPAM.length == 0 && SUSPICIOUS_HAM.length == 0 &&
      NEXT_URL == null) {
      $moreComments.remove();
    } else {
      unlockMoreCommentsButton();
    }
  }).fail(function(data) {
    $moreComments.remove();
    console.log('ERROR JSON!!!');
    console.log(data.responseText);
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

function suspiciousComment(content) {
  var fixed = content.replace(/ /g,'').toLowerCase();

  if (fixed.indexOf('visit') != -1 || fixed.indexOf('.co') != -1 ||
      fixed.indexOf('http') != -1 || fixed.indexOf('buy') != -1 ||
      fixed.indexOf('site') != -1 || fixed.indexOf('subscrib') != -1) {
    return true;
  }
  return false;
}

function saveComment(saveButton) {
  var $root = saveButton.parent().parent();
  var comment_id = $root.attr('comment_id');
  var tag = saveButton.attr('tag');
  var content = $root.find('.comment_content').html();

  $.ajax({
    type: 'POST',
    url: '/saveComment',
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: {comment_id: comment_id,
        video_id: VIDEO_ID,
        content: content,
        tag: tag },
    dataType: 'text'
  }).done(function(success) {
    var sibling = saveButton.siblings();
    saveButton.attr('disabled', true);

    if (tag == 'spam') {
      incrementCounter($spamCount);
      if ($root.attr('tagType') == 'manual') {
        decrementCounter($hamCount);
      } else {
        incrementCounter($taggedCount);
      }
      saveButton.addClass('alert');
      sibling.removeClass('success');

    } else {
      incrementCounter($hamCount);
      if ($root.attr('tagType') == 'manual') {
        decrementCounter($spamCount);
      } else {
        incrementCounter($taggedCount);
      }
      saveButton.addClass('success');
      sibling.removeClass('alert');
    }

    sibling.removeAttr('disabled');
    console.log(success);
  });
}

function exportComments() {
  $('#export-form').submit();
}

$(document).ready(function(){
  /* Initializing some global variables */
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video_title').attr('video_id');

  $('#comments').children('.comment[tagType=manual]').each(function() {
    TAGGED_COMMENTS[$(this).attr('comment_id')] = $(this).attr('comment_id');
  });

  /* Retrieving first informations */
  getVideoMeta(VIDEO_ID);
  NEXT_URL = 'https://gdata.youtube.com/feeds/api/videos/'+ VIDEO_ID +
             '/comments?alt=json&max-results=50&orderby=published';

  //function getNewComments(nextHandler, total_length, spam_length, ham_length)
  getNewComments(sendToClassifier, 500, 40, 60);

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
        getNewComments(sendToClassifier, 500, 40, 60);
      } else {
        sendToClassifier();
      }
    }

    return false;
  });

  $('#export-form').submit(function() {

    if ($('#export-button').attr('disabled')) {
      return false;
    }

    $('#export-comments').empty();

    /* Export options:
     * t  => tagged only
     * tu => tagged and untagged
     * tc => tagged and classified
     */
    var exportOption = $('input[name=export-option]:checked', '#export-form').val();
    if (exportOption !== 't') {

      var $exportComments = $('#export-comments');
      var $commentsChildrenAutomatic = $('#comments').children('.comment[tagType=automatic]');
      var newComment;
      var total_length = 1000;
      var spam_length = 1000;
      var ham_length = 1000;

      /* If there is not enough untagged comments, fetching new comments */
      if (($commentsChildrenAutomatic.length + SUSPICIOUS_SPAM.length + SUSPICIOUS_HAM.length < total_length) &&
          (NEXT_URL != null)) {
        getNewComments(exportComments, total_length, spam_length, ham_length);
        return false;
      }

      /* Handling comments already displayed */
      $commentsChildrenAutomatic.each(function() {

        newComment = {comment_id: $(this).attr('comment_id'),
                      content: $(this).find('.comment_content').html()};

        newComment = JSON.stringify(newComment).replace(/"/g, '&quot;');
        $exportComments.append('<input type="hidden" name="comments" value="'+newComment+'">');
      });

      /* Handling hidden comments */
      var len = SUSPICIOUS_SPAM.length < spam_length ? SUSPICIOUS_SPAM.length : spam_length;
      for (var i = 0; i < len; i++) {
        newComment = SUSPICIOUS_SPAM[i];
        newComment = JSON.stringify(newComment).replace(/"/g, '&quot;');
        $exportComments.append('<input type="hidden" name="comments" value="'+newComment+'">');
      }

      len = SUSPICIOUS_HAM.length < ham_length ? SUSPICIOUS_HAM.length : ham_length;
      for (var i = 0; i < len; i++) {
        newComment = SUSPICIOUS_HAM[i];
        newComment = JSON.stringify(newComment).replace(/"/g, '&quot;');
        $exportComments.append('<input type="hidden" name="comments" value="'+newComment+'">');
      }
    }

  });

});