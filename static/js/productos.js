$(function () {

    const $panel = $('#productoFormPanel');
    const $form = $('#formProducto');
    const createUrl = $form.data('create-url');

    function mostrarFormularioProducto() {
        $panel.show();
        $('html, body').animate({ scrollTop: $panel.offset().top - 20 }, 200);
    }

    function ocultarFormularioProducto() {
        $panel.hide();
        // reset form
        $form.attr('action', createUrl);
        $form[0].reset();
    }

    // initial state: hide
    $panel.hide();

    $('#btnNuevoProducto').on('click', function () {
        // set to create
        $form.attr('action', createUrl);
        $form[0].reset();
        mostrarFormularioProducto();
    });

    $(document).on('click', '#btnCerrarProducto', function () {
        ocultarFormularioProducto();
    });

    // Edit button handler
    $(document).on('click', '.btnEditarProducto', function () {
        const $btn = $(this);
        const action = $btn.data('action');
        const codigo = $btn.data('codigo');
        const nombre = $btn.data('nombre');
        const categoria = $btn.data('categoria');
        const stock = $btn.data('stock');

        // populate form
        $('#id_codigo').val(codigo);
        $('#id_nombre').val(nombre);
        $('#id_stock').val(stock);
        $('#id_categoria').val(categoria);

        $form.attr('action', action);
        mostrarFormularioProducto();
    });

});
