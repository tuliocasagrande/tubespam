function getVideoMeta(video_id) {
  var url = 'https://gdata.youtube.com/feeds/api/videos/'+ video_id +'?alt=json';
  $.ajax({
    type: 'GET',
    url: url,
    dataType: 'json'
  }).done(function(data){
    document.title = data.entry.title.$t;
    $('#video_title').html(data.entry.title.$t);
    $('#published').html(formattedDate(new Date(data.entry.published.$t)));
    $('#content').html(data.entry.content.$t);

    $('#viewCount').html(formattedNumber(data.entry.yt$statistics.viewCount));

    try {
      COMMENT_COUNT = data.entry.gd$comments.gd$feedLink.countHint;
      $('#commentCount').html(formattedNumber(COMMENT_COUNT));
      getTaggedComments(video_id);
    } catch(e) {
      $('#comments').append("Comments are disabled for this video.");
      $moreComments.remove();
    }
  });
}

var $moreComments = $('#moreComments');
function lockMoreCommentsButton() {
  $moreComments.html('Loading ...');
  $moreComments.attr('disabled', true);
}

function unlockMoreCommentsButton() {
  $moreComments.html('Show more comments <i class="fi-refresh"></i>');
  $moreComments.removeAttr('disabled');
}

var $taggedCount = $('#taggedCount');
var $spamCount = $('#spamCount');
var $hamCount = $('#hamCount');

function updateTagsCount() {
  $taggedCount.html(formattedNumber(NUMBER_OF_TAGGED));
  $spamCount.html(formattedNumber(NUMBER_OF_TAGGED_SPAM));
  $hamCount.html(formattedNumber(NUMBER_OF_TAGGED_HAM));
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

function formattedDate(date) {
  var MONTH_NAMES = ["Jan ", "Feb ", "Mar ", "Apr ", "May ", "Jun ",
                     "Jul ", "Aug ", "Sep ", "Oct ", "Nov ", "Dec "];

  return 'Uploaded on ' + MONTH_NAMES[date.getMonth()] + date.getDate() + ', ' + date.getFullYear();
}

var TAGGED_COMMENTS;
var NUMBER_OF_TAGGED = 0;
var NUMBER_OF_TAGGED_SPAM = 0;
var NUMBER_OF_TAGGED_HAM = 0;

var SUSPICIOUS_SPAM = [];
var SUSPICIOUS_HAM = [];

var BUTTON = 'comment_tag right tiny secondary button';
var NEXT_FEED;
var COMMENT_COUNT = 0;

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

function formattedComment(id, content, tag, tagType) {
  tagType = typeof tagType !== 'undefined' ? tagType : '';

  var comment = '<div class="comment row" tagType="'+ tagType +'" comment_id="'+ id +'">' +
                '<p class="content small-9 columns">'+ content +'</p>' +
                tag +'</div><hr/>';

  return comment;
}

function getTaggedComments(video_id) {

  $.ajax({
    type: 'GET',
    url: '/getTaggedComments',
    data: { v: video_id },
    dataType: 'json'
  }).done(function(data) {
    TAGGED_COMMENTS = data;

    for (var key in TAGGED_COMMENTS) {
      if (TAGGED_COMMENTS[key].tag === "1") {
        NUMBER_OF_TAGGED_SPAM++;
        $('#comments').prepend(formattedComment(key,
          TAGGED_COMMENTS[key].content, SPAM_TAG, 'manual'));
      } else {
        NUMBER_OF_TAGGED_HAM++;
        $('#comments').prepend(formattedComment(key,
          TAGGED_COMMENTS[key].content, HAM_TAG, 'manual'));
      }
      NUMBER_OF_TAGGED++;
    }
    updateTagsCount();

    var url = 'https://gdata.youtube.com/feeds/api/videos/'+ video_id +'/comments?' +
            'alt=json&max-results=50&orderby=published';
    getNewComments(url);
  }).fail(function(data) {
    console.log('ERROR JSON!!!');
    console.log(data.responseText);
  })
}


function getNewComments(url) {

  $.ajax({
    type: 'GET',
    url: url,
    dataType: 'json'
  }).fail(function() {
    $('#comments').append("Comments are disabled for this video.");
    $moreComments.remove();
  }).done(function(data){
    loadNewComments(data);

    if (data.feed.link[data.feed.link.length-1].rel == 'next') {
      NEXT_FEED = data.feed.link[data.feed.link.length-1].href;
    } else {
      NEXT_FEED = null;
      putNewComments();
      return;
    }

    if (SUSPICIOUS_SPAM.length > 20 && SUSPICIOUS_HAM.length > 30) {
      putNewComments();
      return;
    }

    getNewComments(NEXT_FEED);
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
    } else if (content === '') {
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

function putNewComments() {
  appendToHtml(SUSPICIOUS_SPAM, 20);
  appendToHtml(SUSPICIOUS_HAM, 30);

  if (SUSPICIOUS_SPAM.length == 0 && SUSPICIOUS_HAM.length == 0 &&
      NEXT_FEED == null) {
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
      newComment.comment_id, newComment.content, TAG));
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


$(document).ready(function(){
  var csrftoken = $.cookie('csrftoken');
  var video_id = $('#video_title').attr('video_id');
  getVideoMeta(video_id);

  $('#comments').on('click', '.comment_tag', function() {
    var $this = $(this);

    if ($this.attr('disabled')) {
      return false;
    }

    var $root = $this.parent().parent();
    var comment_id = $root.attr('comment_id');
    var tag = $this.attr('tag');
    var content = $root.find('.content').html();

    $.ajax({
      type: 'POST',
      url: '/saveComment',
      headers: {'X-CSRFToken': csrftoken},
      data: {comment_id: comment_id,
          video_id: video_id,
          content: content,
          tag: tag },
      dataType: 'text'
    }).done(function(success) {
      if (tag == 'spam') {
        NUMBER_OF_TAGGED_SPAM++;
        if ($root.attr('tagType') == 'manual') {
          NUMBER_OF_TAGGED_HAM--;
        } else {
          NUMBER_OF_TAGGED++;
        }
        $this.siblings().removeClass('success');
        $this.addClass('alert');

      } else {
        NUMBER_OF_TAGGED_HAM++;
        if ($root.attr('tagType') == 'manual') {
          NUMBER_OF_TAGGED_SPAM--;
        } else {
          NUMBER_OF_TAGGED++;
        }
        $this.siblings().removeClass('alert');
        $this.addClass('success');
      }

      $this.siblings().removeAttr('disabled');
      $this.attr('disabled', true);
      updateTagsCount();
      console.log(success);
    });
  });

  $('#moreComments').click(function() {
    if (!$(this).attr('disabled')) {
      console.log('More comments...');

      if (NEXT_FEED != null) {
        lockMoreCommentsButton();
        getNewComments(NEXT_FEED);
      } else {
        putNewComments();
      }
    }

    return false;
  });

});
