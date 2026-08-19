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
        $('#id_codigo').val($btn.attr('data-codigo'));
        $('#id_nombre').val($btn.attr('data-nombre'));
        $('#id_descripcion').val($btn.attr('data-descripcion'));
        $('#id_categoria').val($btn.attr('data-categoria'));
        $('#id_clasificacion_tributaria').val($btn.attr('data-clasificacion-tributaria'));
        $('#id_costo').val($btn.attr('data-costo').replace(',', '.'));
        $('#id_precio').val($btn.attr('data-precio').replace(',', '.'));
        $('#id_stock').val($btn.attr('data-stock'));
        $('#id_stock_minimo').val($btn.attr('data-stock-minimo'));
        $('#id_estado').prop('checked', $btn.attr('data-estado') === 'true');

        $form.attr('action', action);
        mostrarFormularioProducto();
    });

});
