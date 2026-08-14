$(document).ready(function () {
    console.log("detalle_entrada.js cargado");

    //==========================================
    // DATATABLE
    //==========================================

    $('#tablaDetalleEntrada').DataTable({

        responsive: true,

        pageLength: 10,

        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json"
        }

    });


    //==========================================
    // VARIABLES
    //==========================================

    let modoEditar = false;

    const urlAgregar = $('#formDetalle').attr('action');


    //==========================================
    // CALCULAR SUBTOTAL
    //==========================================

    function calcularSubtotal() {

        let cantidad = parseFloat($('#id_cantidad').val()) || 0;

        let costo = parseFloat($('#id_costo').val()) || 0;

        let subtotal = cantidad * costo;

        $('#id_subtotal').val("$ " + subtotal.toFixed(2));

    }


    $('#id_cantidad, #id_costo').on(
        'keyup change',
        calcularSubtotal
    );


    //==========================================
    // NUEVO PRODUCTO
    //==========================================

    $(document).on('click', '#btnNuevoDetalle', function () {

        modoEditar = false;

    });


    //==========================================
    // CUANDO SE ABRE EL MODAL
    //==========================================

    $('#detalleModal').on('show.bs.modal', function () {

        if (!modoEditar) {

            $('#tituloDetalle').text("Agregar Producto");

            $('#btnGuardarDetalle').html(
                '<i class="bi bi-save"></i> Guardar Producto'
            );

            $('#formDetalle').attr(
                'action',
                urlAgregar
            );

            $('#formDetalle')[0].reset();

            $('#detalle_id').val("");

            $('#id_cantidad').val(1);

            $('#id_subtotal').val("$ 0.00");

        }

    });


    //==========================================
    // EDITAR PRODUCTO
    //==========================================

    $(document).on('click', '.btnEditarDetalle', function () {

        console.log("EDITAR");

        console.log($(this).data());

        modoEditar = true;

        console.log($(this).data());

        $('#tituloDetalle').text("Editar Producto");

        $('#btnGuardarDetalle').html(
            '<i class="bi bi-pencil-square"></i> Actualizar Producto'
        );

        $('#formDetalle').attr(
            'action',
            $(this).data('url')
        );

        $('#detalle_id').val(
            $(this).data('id')
        );

        $('#id_producto').val(
            $(this).data('producto')
        );

        $('#id_cantidad').val(
            $(this).data('cantidad')
        );

        $('#id_costo').val(
            $(this).data('costo')
        );

        calcularSubtotal();

    });


    //==========================================
    // CUANDO SE CIERRA EL MODAL
    //==========================================

    $('#detalleModal').on('hidden.bs.modal', function () {

        modoEditar = false;

        $('#formDetalle')[0].reset();

        $('#detalle_id').val("");

        $('#id_subtotal').val("$ 0.00");

    });


    //==========================================
    // VALIDACIONES
    //==========================================

    $('#formDetalle').submit(function (e) {

        let valido = true;

        $('.is-invalid').removeClass('is-invalid');

        if ($('#id_producto').val() === "") {

            $('#id_producto').addClass('is-invalid');

            valido = false;

        }

        if (
            $('#id_cantidad').val() === "" ||
            parseInt($('#id_cantidad').val()) <= 0
        ) {

            $('#id_cantidad').addClass('is-invalid');

            valido = false;

        }

        if (
            $('#id_costo').val() === "" ||
            parseFloat($('#id_costo').val()) <= 0
        ) {

            $('#id_costo').addClass('is-invalid');

            valido = false;

        }

        if (!valido) {

            e.preventDefault();

            Swal.fire({

                icon: "warning",

                title: "Información incompleta",

                text: "Complete correctamente todos los campos."

            });

        }

    });
    // =====================================
    // ELIMINAR DETALLE DE ENTRADA
    // =====================================

        document.querySelectorAll(
    ".btnEliminarDetalle"
        ).forEach(
        boton => {


        boton.addEventListener(
        "click",
        function(){


        const url =
        this.dataset.url;



        const formulario =
        document.getElementById(
            "formEliminarDetalleEntrada"
        );



        if(formulario){

            formulario.action = url;

        }



    });


});


});