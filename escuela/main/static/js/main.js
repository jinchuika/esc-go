function comprar_paquete(form) {
	var form_data = $(form).serializeArray();
	console.log($(form));
	$.ajax({
		url: 'comprar/',
		type: 'POST',
		data: {
			csrfmiddlewaretoken: form_data[0].value,
			paquete_id: form_data[1].value
		},
		success: function (json) {
			if (json['done']==1) {
				BootstrapDialog.alert('¡Apoyaste con éxito!');
			}
			$('.tokens-activos').html(json.tokens)
		}
	})
}

function profile_detail_chart(form) {
	var form_data = $(form).serializeArray();
	$.ajax({
		url: 'chart/',
		type: 'POST',
		data: {
			csrfmiddlewaretoken: form_data[0].value,
			id_profile: form_data[1].value
		},
		success: function (respuesta) {
			var ctx = document.getElementById("chart-canvas").getContext("2d");
			var data = {
				labels: respuesta.materia,
				datasets: [
				{
					label: "Lugar",
					type: "line",
					fill: false,
					lineTension: 0.1,
					borderColor: "rgba(75,192,192,1)",
					pointBackgroundColor: "#fff",
					pointHoverRadius: 10,
					pointHoverBackgroundColor: "rgba(75,192,192,1)",
					pointRadius: 5,
					pointHitRadius: 10,
					data: respuesta.lugar,
					spanGaps: false,
					yAxisID: 'y-axis-1'
				},
				{
					label: "Puntos",
					type: "line",
					fill: false,
					lineTension: 0.1,
					borderColor: "rgba(113, 179, 124,1)",
					pointBackgroundColor: "#fff",
					pointHoverRadius: 10,
					pointHoverBackgroundColor: "rgba(113, 179, 124,1)",
					pointRadius: 5,
					pointHitRadius: 10,
					data: respuesta.puntos,
					spanGaps: false,
					yAxisID: 'y-axis-2'
				}
				]
			};
			var myLineChart = new Chart(ctx, {
				type: 'bar',
				data: data,

				options: {
					tooltips: {
                  mode: 'x-axis'
              },
					scales: {
						xAxes: [{
							display: true
						}],
						yAxes: [
						{
							reverse: true,
							id: "y-axis-1",
							ticks: {
								stepSize: 2,
								fixedStepSize: 1,
								reverse: true
							}
						},
						{
							id: "y-axis-2",
							display: false,
							ticks: {
								stepSize: 2,
								fixedStepSize: 1,
							}
						}
						]
					}
				}
			});
		}
	})
}

$(document).ready(function () {
	$('.form-compra').on('submit', function (e) {
		var formulario = $(this);
		e.preventDefault();
		BootstrapDialog.confirm('Confirma que deseas comprar '+formulario.data('tokens')+' token(s) por $'+formulario.data('precio'), function(result){
			if(result) {
				comprar_paquete(formulario);
			}else {
			}
		});
	});

	$('.form-apuesta').on('submit', function (e) {
		var formulario = $(this);
		e.preventDefault();
		BootstrapDialog.confirm('Confirma que deseas apoyar con '+$('#id_tokens').val()+' token(s)', function(result){
			if(result) {
				$(formulario).off('submit').trigger('submit');
			}
		});
	})

	$('.table-paginated').DataTable({
		searching: false,
		lengthChange: false,
		"language": {
			"lengthMenu": "Mostrar _MENU_ registros por página",
			"zeroRecords": "No hay información",
			"info": "Mostrando página _PAGE_ de _PAGES_",
			"infoEmpty": "No se encontraron registros",
			"infoFiltered": "(filtrado de _MAX_ registros en total)",
			"paginate": {
				"first":      "Primero",
				"last":       "Último",
				"next":       "Siguiente",
				"previous":   "Anterior"
			},
		}
	});

	$('#form-profile-chart').on('submit', function (e) {
		e.preventDefault();
		profile_detail_chart($(this));
	});
});