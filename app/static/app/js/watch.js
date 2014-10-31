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

function formattedComment(comment_id, author, date, content, tag, tagType) {
  tagType = typeof tagType !== 'undefined' ? tagType : '';

  var comment = '<div class="comment row" tagType="'+ tagType +'" comment_id="'+ comment_id +'">' +
                '<p class="comment_header small-12 columns">' +
                '<strong class="comment_author">'+ author +'</strong>'+
                '<a href="https://www.youtube.com/watch?v='+ VIDEO_ID +'&google_comment_id='+comment_id+'" target="_blank">' +
                '<small class="comment_date">'+ date +'</small></a></p>' +
                '<p class="comment_content small-9 columns">'+ content +'</p>' +
                tag +'</div><hr/>';

  return comment;
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
    $('#video_publish_date').html('Published on ' + new Date(data.entry.published.$t).toUTCString());
    $('#video_content').html(data.entry.content.$t);

    $('#viewCount').html(formattedNumber(data.entry.yt$statistics.viewCount));

    try {
      var commentCount = data.entry.gd$comments.gd$feedLink.countHint;
      $('#commentCount').html(formattedNumber(commentCount));
    } catch(e) {
      console.log(e);
      $('#comments').append("Comments are disabled for this video.");
      $moreComments.remove();
    }
  });
}

function getNewComments(url, call) {

  $.ajax({
    type: 'GET',
    url: url,
    dataType: 'json'
  }).fail(function() {
    // This usually happens when the api receives too many hits
    console.log('Something went wrong. Trying again in few seconds.');
    setTimeout(function(){ getNewComments(url, call) }, 3000);

  }).done(function(data){
    loadNewComments(data);
    console.log(SUSPICIOUS_SPAM.length + SUSPICIOUS_HAM.length);

    var last_link = data.feed.link.length - 1;
    if (data.feed.link[last_link].rel == 'next') {
      NEXT_URL = data.feed.link[last_link].href;
    } else {
      NEXT_URL = null;
      putNewComments();
      return;
    }

    if (call > 20 || (SUSPICIOUS_SPAM.length > 20 && SUSPICIOUS_HAM.length > 30)) {
      putNewComments();
      return;
    }

    getNewComments(NEXT_URL, call+1);
  });
}


function loadNewComments(data) {
  var len, start_index, comment_id, author, date, content, newComment;

  try {
    len = data.feed.entry.length;
  } catch(e) {
    console.log(e);
    len = 0;
  }

  for (var i = 0; i < len; i++) {
    start_index = data.feed.entry[i].id.$t.lastIndexOf('/') + 1;
    comment_id = data.feed.entry[i].id.$t.substring(start_index);
    author = data.feed.entry[i].author[0].name.$t;
    date = new Date(data.feed.entry[i].published.$t).toUTCString();
    content = data.feed.entry[i].content.$t;

    if (TAGGED_COMMENTS.hasOwnProperty(comment_id)) {
      continue;
    } else if (!content.trim()) {
      continue;
    }

    newComment = {comment_id: comment_id, author: author, date: date, content: content};
    if (suspiciousComment(content)) {
      SUSPICIOUS_SPAM.push(newComment);
    } else {
      SUSPICIOUS_HAM.push(newComment);
    }
  }
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
  var author = $root.find('.comment_author').html();
  var date = $root.find('.comment_date').html();

  $.ajax({
    type: 'POST',
    url: '/saveComment',
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: {comment_id: comment_id,
        video_id: VIDEO_ID,
        author: author,
        date: date,
        content: content,
        tag: tag },
    dataType: 'text'
  }).done(function(success) {
    var sibling = saveButton.siblings();

    if (tag == 'spam') {
      incrementCounter($spamCount);
      if ($root.attr('tagType') == 'manual') {
        decrementCounter($hamCount);
      } else {
        incrementCounter($classifiedCount);
      }
      saveButton.addClass('alert');
      sibling.removeClass('success');

    } else {
      incrementCounter($hamCount);
      if ($root.attr('tagType') == 'manual') {
        decrementCounter($spamCount);
      } else {
        incrementCounter($classifiedCount);
      }
      saveButton.addClass('success');
      sibling.removeClass('alert');
    }

    saveButton.attr('disabled', true);
    sibling.removeAttr('disabled');
    $root.attr('tagType', 'manual');

    if (parseInt($spamCount.attr('value')) >= 10 && parseInt($hamCount.attr('value')) >= 10) {
      $('#classify-button').removeAttr('disabled');
    } else {
      $('#classify-button').attr('disabled', true);
    }

    console.log(success);
  });
}

$(document).ready(function(){
  //var CSRFTOKEN = $('[name="csrfmiddlewaretoken"]').val();
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video_title').attr('video_id');

  $('#comments').children('.comment[tagType=manual]').each(function() {
    TAGGED_COMMENTS[$(this).attr('comment_id')] = $(this).attr('comment_id');
  });

  getVideoMeta(VIDEO_ID);
  var url = 'https://gdata.youtube.com/feeds/api/videos/'+ VIDEO_ID +'/comments?' +
            'alt=json&max-results=50&orderby=published';
  getNewComments(url, 0);

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
        getNewComments(NEXT_URL, 0);
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

});
