var csrf = $("#csrf").val();

function addTeamValues(placing, name, con, div, rank) {
	var html = '<tr>';
	html += '<td data-type="team" data-value="'+name.toLowerCase()+'"><span>'+name+'</span></td>'
	html += '<td data-type="con" data-value="'+con.toLowerCase()+'"><span>'+con+'</span></td>'
	html += '<td data-type="div" data-value="'+div.toLowerCase()+'"><span>'+div+'</span></td>'
	html += '<td data-type="rank" data-value="'+rank.toLowerCase()+'"><div><div>'+rank+'</div></div></td>';
	html += '<td data-type="action" data-value="remove_row"><div><div>x</div></div></td>';
	html += '</tr>'
	if(placing == 'before') 
		$('table tbody tr.input-row').after(html);
	else if(placing == 'after')
		$('table tbody').append(html);
}

$('#add_team').on('submit', function(e) {
	e.preventDefault();
	var $row = $(this).parent();
	var $name = $('input[name=new-name]', $row);
	var $con = $('input[name=new-con]', $row);
	var $div = $('input[name=new-div]', $row);
	var $rank = $('input[name=new-rank]', $row);

	var error = false;

	if($name.val() == '' || $name.val().length < 2) {
		$name.parents('td.input-cell').addClass('error');
		error = true;
	}
	if($con.val() == '' || $con.val().length < 2) {
		$con.parents('td.input-cell').addClass('error');
		error = true;
	}
	if($div.val() == '' || $div.val().length < 2) {
		$div.parents('td.input-cell').addClass('error');
		error = true;
	}
	if($rank.val() == '' || $rank.val().length < 1
		|| $rank.val() == 0 || $rank.val() == '0') {
		$rank.parents('td.input-cell').addClass('error');
		error = true;
	}

	if(error) {
		return;
	}
	else {
		addTeamValues('before', $name.val(),$con.val(),$div.val(),$rank.val());
		$name.val('');
		$name.removeClass('error');
		$name.focus();
		$con.val('');
		$con.removeClass('error');
		$div.val('');
		$div.removeClass('error');
		$rank.val('');
		$rank.removeClass('error');
	}
});

$('tbody').on('click', 'td[data-type=action][data-value=remove_row]', function() {
	$(this).parents('tr').remove();
});

// IMPORT /////////////////////////////////////////
$('.control-group .hidden-input-toggle').on('click', submit_import);
$('#import_form').on('submit', function(e) {
	e.preventDefault();
	e.stopPropagation();
	submit_import();
});

function submit_import() {
  var $input = $('#import_form .hidden-input');
  if($input.val().length == 0) return;

  var submit_url = $('#import_form').attr('url');
  var sheet_url = $input.val();
  var form = $(this);

  if(sheet_url == '' || sheet_url.length == 0) {
  	form.after('<p>Enter a URL</p>');
  	return
  }

  send_data = {
      sheet_url: sheet_url,
      csrfmiddlewaretoken: csrf
  };

  $.ajax({
    url: submit_url,   
    data: send_data,
    type: "POST",
    dataType : "json",
    success: function(json) {
      if (!json.error) {
        $input.val('');
        $input.blur();
        $input.animate({width: 'toggle'}, 250);
        for (var i = 0; i < json.values.length; i++) {
		    var team = json.values[i];
		    addTeamValues('after', team[0], team[1], team[2], team[3]);
		}
      }
      else {
      	alert(json.error_message);
      }
    },
    error: function(xhr, status, errorThrown) {
        alert("Error: " + errorThrown);
    },
    complete: function( xhr, status ) {
      return;
    }
  });
}

$('.generate').on('click', function() {
	var $table = $('table.table-schedule-new tbody');
	if($table.children().length <= 2) {
		alert('Not enough teams to generate a schedule.');
		return;
	}
	var teams = [];
	var exit = false;
	$('tr:not(.input-row)', $table).each(function() {
		if(exit) { return; }
		var name = $('td[data-type=team] > span', $(this)).html();
		var con = $('td[data-type=con]', $(this)).attr('data-value');
		var div = $('td[data-type=div]', $(this)).attr('data-value');
		var rank = $('td[data-type=rank]', $(this)).attr('data-value');
		if(name == null || name.length == 0
			|| con == null || con.length == 0
			|| div == null || div.length == 0
			|| rank == null || rank.length == 0) {
			alert(name+ 'You cannot have empty fields.');
			exit = true;
			return;
		}
		for(var i=0; i<teams.length; i++) {
			if(teams[i][0].toLowerCase() == name.toLowerCase()) {
				alert('Duplicate teams ('+name+'). Please remove one.');
				exit = true;
				return;
			}
		}
		teams.push([name, con, div, rank]);
	});
	if(exit) { return; }

	var to_gen = $('.schedule-info input[name=to_gen]').val()
	var total = $('.schedule-info input[name=total]').val()
	var algo = $('.schedule-info select[name=algo] option:selected').val()
	var season = $('.schedule-info select[name=season] option:selected').val()
	var year = $('.schedule-info select[name=year] option:selected').val()
	var name = $('.schedule-info input[name=name]').val()
	var override = true;
	var schedule_id = null;

	if(total==null || total.toString().length == 0 || parseInt(total) <= 0) {
		alert('Invalid total number of games');
		return;
	}

	if(to_gen==null || to_gen.toString().length == 0 || parseInt(to_gen) <= 0 || parseInt(to_gen) > parseInt(total)) {
		alert('Invalid value for number of games to generate');
		return;
	}

	if(algo==null || algo.toString().length != 1 || parseInt(algo) < 0 || parseInt(algo
		) >= 3 ) {
		alert('Invalid matching method');
		return;
	}

	if(season==null || season.length < 4) {
		alert('Invalid season');
		return;
	}

	if(year==null || year.toString().length != 4 || parseInt(year) < 1900) {
		alert('Invalid year');
		return;
	}

	if(name==null || name.toString().length == 0) {
		name = "Untitled"
	}
	
	$('#part2-content').fadeOut(250, function() {
		$('#part3-loader').fadeIn(250);
	});
	$('#part2-subtitle').fadeOut(250);

	send_data = {
      teams: JSON.stringify(teams),
      to_gen: to_gen,
      total: total,
      algo: algo,
      season: season,
      year: year,
      name: name,
      override: override,
      schedule_id: schedule_id,
      csrfmiddlewaretoken: csrf
	};

	var $button = $(this);

	$.ajax({
		url: $button.attr('url'),   
		data: send_data,
		type: "POST",
		dataType : "json",
		success: function(json) {
			if (!json.error) {
				window.location.href = $button.attr('return-url').replace('0', json.schedule_id);
			}
			else {
				$('#part3-loader').fadeOut(250, function() {
					$('#part2-content').fadeIn(250);
					$('#part2-subtitle').fadeIn(250);
				});
				alert(json.error_message);
			}
		},
		error: function(xhr, status, errorThrown) {
			setTimeout(function() {
				$('#part3-loader').fadeOut(250, function() {
					$('#part2-content').fadeIn(250);
					$('#part2-subtitle').fadeIn(250);
				});
				alert("Error: " + errorThrown);
			}, 500);
		},
		complete: function( xhr, status ) {
			return;
		}
	});
});