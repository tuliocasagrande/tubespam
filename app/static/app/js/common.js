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

function formattedComment(comment_id, author, date, content, tag, tag_type) {
  tag_type = typeof tag_type !== 'undefined' ? tag_type : '';

  var comment = '<div class="comment-row row" tag-type="'+ tag_type +'" comment-id="'+ comment_id +'">' +
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

// Multiple replaces is the fastest way. Do not change!
function safe_tags(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function lockLoadingButton($button, text_change) {
  if (text_change) $button.html(text_change);
  $button.addClass('loading-icon');
  $button.prop('disabled', true);
}
function unlockLoadingButton($button, text_change) {
  if (text_change) $button.html(text_change);
  $button.removeClass('loading-icon');
  $button.prop('disabled', false);
}

function saveComment($save_button) {
  if ($save_button.attr('disabled')) return;

  var $root = $save_button.parent().parent();

  var comment_id = $root.attr('comment-id');
  var tag = $save_button.attr('tag');
  var content = $root.find('.comment_content').html();
  var author = $root.find('.comment_author').html();
  var date = $root.find('.comment_date').html();

  $.ajax({
    type: 'POST',
    url: SAVECOMMENT_AJAX_URL,
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: {comment_id: comment_id,
        v: VIDEO_ID,
        channel_id: CHANNEL_ID,
        author: author,
        date: date,
        content: content,
        tag: tag },
    dataType: 'text'
  }).fail(function(data) {
    console.log(data.responseText);

  }).done(function() {
    var sibling = $save_button.siblings();

    if (tag == '1') {
      incrementCounter($spam_count);
      if ($root.attr('tag-type') == 'manual') {
        decrementCounter($ham_count);
      } else {
        incrementCounter($classified_count);
      }
      $save_button.addClass('alert');
      sibling.removeClass('success');

    } else {
      incrementCounter($ham_count);
      if ($root.attr('tag-type') == 'manual') {
        decrementCounter($spam_count);
      } else {
        incrementCounter($classified_count);
      }
      $save_button.addClass('success');
      sibling.removeClass('alert');
    }

    $save_button.attr('disabled', true);
    sibling.removeAttr('disabled');
    $root.attr('tag-type', 'manual');
  });
}

function predict() {
  $.ajax({
    type: 'GET',
    url: PREDICT_AJAX_URL,
    headers: {'X-CSRFToken': CSRFTOKEN},
    data: { v: VIDEO_ID,
            channel_id: CHANNEL_ID,
            tag: TAG_BOOL,
            next_page_token: NEXT_PAGE_TOKEN },
    dataType: 'json'
  }).fail(function(data) {
    $more_comments.remove();
    $('#export-modal-button').remove();
    try {
      if ($.parseJSON(data.responseText).error.errors[0].reason === 'commentsDisabled')
        $('#predicted-comments').append('<div data-alert class="alert-box alert text-center"><strong>This video has disabled comments!!!</strong></div>');
    } catch (e) {
      console.log(data);
    }
  }).done(function(data) {
    NEXT_PAGE_TOKEN = data['next_page_token'];
    var tag = (TAG_BOOL) ? SPAM_TAG : HAM_TAG;
    for (var key in data['comments']) {
      var c = data['comments'][key];
      $('#predicted-comments').append(formattedComment(key, c.author, c.date,
                                      c.content, tag, 'automatic'));
    }

    if (NEXT_PAGE_TOKEN == 'False') {
      $more_comments.remove();
    } else {
      unlockLoadingButton($more_comments, 'Show more comments <i class="fi-refresh"></i>');
    }
  });
}

var TAG = '<div class="tag-column small-3 columns">' +
          '<span class="comment_tag right tiny secondary button spam" tag="1">Spam</span>' +
          '<span class="comment_tag right tiny secondary button ham" tag="0">Ham</span>' +
          '</div>';

var SPAM_TAG = '<div class="tag-column small-3 columns">' +
          '<span class="comment_tag right tiny secondary button alert spam" disabled tag="1">Spam</span>' +
          '<span class="comment_tag right tiny secondary button ham" tag="0">Ham</span>' +
          '</div>';

var HAM_TAG = '<div class="tag-column small-3 columns">' +
          '<span class="comment_tag right tiny secondary button spam" tag="1">Spam</span>' +
          '<span class="comment_tag right tiny secondary button success ham" disabled tag="0">Ham</span>' +
          '</div>';

var VIDEO_ID;
var CHANNEL_ID;
var CSRFTOKEN;
var NEXT_PAGE_TOKEN;
var $more_comments;
var $classified_count;
var $spam_count;
var $ham_count;

$(function() {
  /* Initializing some global variables */
  CSRFTOKEN = $.cookie('csrftoken');
  VIDEO_ID = $('#video-title').attr('video-id');
  CHANNEL_ID = $('#video-title').attr('channel-id');
  NEXT_PAGE_TOKEN = 'None'

  $more_comments = $('#more-comments');
  $classified_count = $('.classifiedCount');
  $spam_count = $('#spamCount');
  $ham_count = $('#hamCount');

  /* Events listeners */
  $('.comments-section').on('click', '.comment_tag', function() {
    saveComment($(this));
    return false;
  });

  $more_comments.click(function() {
    lockLoadingButton($more_comments, 'Loading ...');
    predict();
    return false;
  });

  $('input[name=export-option]').change(function() {
    var exportOption = $('input[name=export-option]:checked', '#export-form').val();
    if (exportOption === 'm') {
      $('.ext-options-text').addClass('disabled');
      $('.ext-options').prop('disabled', true);
    } else {
      $('.ext-options-text').removeClass('disabled');
      $('.ext-options').prop('disabled', false)
    }
  });
  $('#export-form').submit(function() {
    $('#export-modal').foundation('reveal', 'close');
    $export_amount = $('#export-amount')
    if ($export_amount.val() > 1000) $export_amount.val(1000);
    if ($export_amount.val() < 0) $export_amount.val(0);
  });

  /* Main function first call */
  predict();
});
