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
});