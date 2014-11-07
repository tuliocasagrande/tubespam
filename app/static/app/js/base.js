// Common functions used by watch.js and classify.js

function formattedComment(comment_id, author, date, content, tag, tag_type) {
  tag_type = typeof tag_type !== 'undefined' ? tag_type : '';

  var comment = '<div class="comment row" tag_type="'+ tag_type +'" comment_id="'+ comment_id +'">' +
                '<p class="comment_header small-12 columns">' +
                '<strong class="comment_author">'+ author +'</strong>'+
                '<a href="https://www.youtube.com/all_comments?v='+ VIDEO_ID +'&google_comment_id='+comment_id+'" target="_blank">' +
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

    // This usually happens when the api receives too many hits
    console.log('Something went wrong. Trying again in few seconds.');
    setTimeout(function(){
      getNewComments(nextHandler, total_length, spam_length, ham_length)
    }, 3000);

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

function loadNewComments(data) {
  var len, start_index, comment_id, author, date, content, new_comment;

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
    content = safe_tags(data.feed.entry[i].content.$t);

    if (TAGGED_COMMENTS.hasOwnProperty(comment_id)) {
      continue;
    } else if (!content.trim()) {
      continue;
    }

    new_comment = {comment_id: comment_id, author: author, date: date, content: content};
    if (suspiciousComment(content)) {
      SUSPICIOUS_SPAM.push(new_comment);
    } else {
      SUSPICIOUS_HAM.push(new_comment);
    }
  }
}

// Multiple replaces is the fastest way. Do not change!
function safe_tags(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
