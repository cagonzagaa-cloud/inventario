$(function () {

    const $panel = $('#categoriaFormPanel');
    const $form = $('#formCategoria');
    const createUrl = $form.data('create-url');

    function mostrarFormularioCategoria() {
        $panel.show();
        $('html, body').animate({ scrollTop: $panel.offset().top - 20 }, 200);
    }

    function ocultarFormularioCategoria() {
        $panel.hide();
        $form.attr('action', createUrl);
        $form[0].reset();
    }

    $panel.hide();

    $('#btnNuevaCategoria').on('click', function () {
        $form.attr('action', createUrl);
        $form[0].reset();
        mostrarFormularioCategoria();
    });

    $(document).on('click', '#btnCerrarCategoria', function () {
        ocultarFormularioCategoria();
    });

    $(document).on('click', '.btnEditarCategoria', function () {
        const $btn = $(this);
        const action = $btn.data('action');
        const nombre = $btn.data('nombre');
        const descripcion = $btn.data('descripcion');

        $('#id_nombre').val(nombre);
        $('#id_descripcion').val(descripcion);

        $form.attr('action', action);
        mostrarFormularioCategoria();
    });

});
