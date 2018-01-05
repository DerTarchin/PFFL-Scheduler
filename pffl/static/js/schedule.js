/* -------------------------------- *
* .table-schedule highlighting
* -------------------------------- */
var $table = $('.table-schedule');
var $tbody = $('> tbody', $table);
var checker = true;

$tbody.on('mouseenter', '> tr:not(.input-row) > td:not([data-type=all])', function() {
    if(checker) {
        var type = $(this).attr('data-type');
        var value = $(this).attr('data-value');
        if(type=="action") {
            $('td', $tbody).addClass('dim');
            $(this).siblings('td[data-type]').removeClass('dim');
        }
        else {
            $('td[data-type='+type+'][data-value="'+value+'"]', $tbody).addClass('highlight highlight-'+type);
            $('td[data-type=all]['+type+'-value="'+value+'"]', $tbody).addClass('highlight highlight-'+type);
            $('> thead td[head-type='+type+']', $table).addClass('highlight');
            $('td:not(.input-cell):not([data-type='+type+'][data-value="'+value+'"])', $tbody).addClass('dim')
        }
    }
});

$tbody.on('mouseleave', '> tr:not(.input-row) > td:not([data-type=all])', function() {
    if(checker) {
        var type = $(this).attr('data-type');
        var value = $(this).attr('data-value');
        if(type=="action") {
            $('td', $tbody).removeClass('dim');
        }
        else {
            $('td[data-type='+type+'][data-value="'+value+'"]', $tbody).removeClass('highlight highlight-'+type);
            $('td[data-type=all]['+type+'-value="'+value+'"]', $tbody).removeClass('highlight highlight-'+type);
            $('> thead > tr > td[head-type='+type+']', $table).removeClass('highlight');
            $('td:not(.input-cell):not([data-type='+type+'][data-value="'+value+'"])', $tbody).removeClass('dim')
        }
    }
});

$tbody.on('mouseenter', '> tr > td[data-type=all]', function() {
    $('td[data-type=all]', $tbody).removeClass('hide-match-type');
});

$tbody.on('mouseleave', '> tr > td[data-type=all]', function() {
    $('td[data-type=all]', $tbody).addClass('hide-match-type');
});

$tbody.on('mouseenter', '> tr > td.input-cell', function() {
    $(this).children('span').children('input').focus();
});

$tbody.on('focus', '> tr > td.input-cell > span > input', function() {
    var type = $(this).parents('td.input-cell').attr('input-type')
    $(this).parents('td.input-cell').addClass('focus');
    $('> thead > tr > td[head-type='+type+']', $table).addClass('highlight');
    $(this).blur(function() {
        $(this).parents('td.input-cell').removeClass('focus');
        $('> thead > tr > td[head-type='+type+']', $table).removeClass('highlight');
    });
});

$tbody.on('mouseenter', '> tr > td[data-type=action]', function() {
    $('> tr > td.input-cell > span > input', $tbody).blur();
});

$('.control-group .hidden-input-toggle').on('click', function(e) {
    var $input = $(this).siblings('.hidden-input');
    if($input.val().length == 0) {
        $input.animate({width: 'toggle'}, 250);
    }
});


function compare() {
    $('td[data-type=all]', $tbody).each(function() {
        var div = $(this).attr('div-value');
        var con = $(this).attr('con-value');
        if($(this).siblings('td[data-type=con]').attr('data-value') != con) {
            $(this).attr('match-type', 'non-con');
        }
        else if($(this).siblings('td[data-type=div]').attr('data-value') != div) {
            $(this).attr('match-type', 'non-div');
        }
        else {
            $(this).attr('match-type', 'in-div');
        }
    });
}

function populateInfoFields() {
    var $season = $('select[name=season]');
    if($season.length) {
        var myDate = new Date();
        var month = myDate.getMonth();
        if(month >= 8 && month < 11)
            $season.append('<option value="fall" selected>Fall</option>');
        else
            $season.append('<option value="fall">Fall</option>');
        if(month >= 11 && month < 2)
            $season.append('<option value="winter" selected>Winter</option>');
        else
            $season.append('<option value="winter">Winter</option>');
        if(month >= 2 && month < 5)
            $season.append('<option value="spring" selected>Spring</option>');
        else
            $season.append('<option value="spring">Spring</option>');
        if(month >= 5 && month < 8)
            $season.append('<option value="summer" selected>Summer</option>');
        else
            $season.append('<option value="summer">Summer</option>');
    }

    var $year = $('select[name=year]');
    var myDate = new Date();
    var year = myDate.getFullYear();
    var selected;
    for(var i = year-1; i < year+5; i++) {
        if(i==year) selected = "selected"
        else selected = "";
        $year.append('<option value="'+i+'" '+selected+'>'+i+'</option>');
    }
}

$(document).ready(function() {
    compare();
    populateInfoFields();
});