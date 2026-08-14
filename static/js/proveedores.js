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
		const codigo = $btn.data('codigo');
		const identificacion = $btn.data('identificacion');
		const razon = $btn.data('razon');
		const nombre = $btn.data('nombre');
		const telefono = $btn.data('telefono');
		const correo = $btn.data('correo');
		const direccion = $btn.data('direccion');

		$('#id_codigo').val(codigo);
		$('#id_identificacion').val(identificacion);
		$('#id_razon_social').val(razon);
		$('#id_nombre_comercial').val(nombre);
		$('#id_telefono').val(telefono);
		$('#id_correo').val(correo);
		$('#id_direccion').val(direccion);

		$form.attr('action', action);
		mostrarFormularioProveedor();
	});

});
