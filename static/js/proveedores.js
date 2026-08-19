$(function () {

	const $panel = $('#proveedorFormPanel');
	const $form = $('#formProveedor');
	const createUrl = $form.data('create-url');

	function mostrarFormularioProveedor() {
		$panel.show();
		$('html, body').animate({ scrollTop: $panel.offset().top - 20 }, 200);
	}

	function ocultarFormularioProveedor() {
		$panel.hide();
		$form.attr('action', createUrl);
		$form[0].reset();
	}

	$panel.hide();

	$('#btnNuevoProveedor').on('click', function () {
		$form.attr('action', createUrl);
		$form[0].reset();
		mostrarFormularioProveedor();
	});

	$(document).on('click', '#btnCerrarProveedor', function () {
		ocultarFormularioProveedor();
	});

	$(document).on('click', '.btnEditarProveedor', function () {
		const $btn = $(this);
		const action = $btn.data('action');
		const fields = ['codigo', 'tipo-identificacion', 'identificacion', 'razon', 'nombre',
			'contacto', 'cargo', 'telefono', 'celular', 'correo', 'sitio-web', 'direccion',
			'provincia', 'canton', 'ciudad', 'codigo-postal', 'condicion-pago', 'cupo-credito', 'observaciones'];
		const ids = ['codigo', 'tipo_identificacion', 'identificacion', 'razon_social', 'nombre_comercial',
			'contacto', 'cargo', 'telefono', 'celular', 'correo', 'sitio_web', 'direccion',
			'provincia', 'canton', 'ciudad', 'codigo_postal', 'condicion_pago', 'cupo_credito', 'observaciones'];
		fields.forEach((name, index) => $('#id_' + ids[index]).val($btn.attr('data-' + name)));
		$('#id_estado').prop('checked', $btn.attr('data-estado') === 'true');

		$form.attr('action', action);
		mostrarFormularioProveedor();
	});

});
