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

});