$(document).ready(function () {

    // ===============================
    // DATATABLE
    // ===============================

    $('#tablaEntradas').DataTable({

        pageLength: 5,

        responsive: true,

        language: {

            url: "https://cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json"

        }

    });


    // ===============================
    // VARIABLE DE CONTROL
    // ===============================

    let modoEditar = false;


    // ===============================
    // NUEVA ENTRADA
    // ===============================

    $('#btnNuevaEntrada').on('click', function () {

        modoEditar = false;

    });


    // ===============================
    // EDITAR ENTRADA
    // ===============================

    $(document).on('click', '.btnEditarEntrada', function () {

        modoEditar = true;

        $('#tituloEntrada').text("Editar Entrada");

        $('#formEntrada').attr(
            "action",
            "/entradas/editar/" + $(this).data("id") + "/"
        );

        $('#id_fecha').val(
            $(this).data("fecha")
        );

        $('#id_proveedor').val(
            $(this).data("proveedor")
        );

        $('#id_numero_documento').val(
            $(this).data("documento")
        );

        $('#id_tipo').val(
            $(this).data("tipo")
        );

        $('#id_operacion_tributaria').prop(
            'checked', $(this).attr('data-operacion-tributaria') === 'true'
        );

        $('#id_observaciones').val(
            $(this).data("observaciones")
        );

        $('#btnGuardarEntrada').html(
            '<i class="bi bi-pencil"></i> Actualizar Entrada'
        );

    });


    // ===============================
    // CUANDO SE ABRE EL MODAL
    // ===============================

    $('#entradaModal').on('show.bs.modal', function () {

        if (!modoEditar) {

            $('#tituloEntrada').text("Nueva Entrada");

            $('#formEntrada').attr(
                "action",
                "/entradas/crear/"
            );

            $('#formEntrada')[0].reset();

            $('#id_tipo').val("COMPRA");

            $('#id_operacion_tributaria').prop('checked', true);

            $('#totalEntrada').val("$ 0.00");

        }

    });


    // ===============================
    // AL CERRAR EL MODAL
    // ===============================

    $('#entradaModal').on('hidden.bs.modal', function () {

        modoEditar = false;

        $('#formEntrada')[0].reset();

        $('.is-invalid').removeClass('is-invalid');

    });


    // ===============================
    // VALIDACIÓN
    // ===============================

    $('#formEntrada').submit(function (e) {

        let valido = true;

        $('.is-invalid').removeClass("is-invalid");

        if ($('#id_fecha').val() === "") {

            $('#id_fecha').addClass("is-invalid");

            valido = false;

        }

        if ($('#id_proveedor').val() === "") {

            $('#id_proveedor').addClass("is-invalid");

            valido = false;

        }

        if (!valido) {

            e.preventDefault();

            Swal.fire({

                icon: "warning",

                title: "Información incompleta",

                text: "Complete los campos obligatorios."

            });

        }

    });


    // ==========================================
    // ELIMINAR ENTRADA
    // ==========================================

    $(document).on('click', '.btnEliminarEntrada', function () {

        let url = $(this).data('url');

        let codigo = $(this).data('codigo');

        Swal.fire({

            title: "¿Eliminar entrada?",

            html: `Se eliminará la entrada <b>${codigo}</b>.`,

            icon: "warning",

            showCancelButton: true,

            confirmButtonColor: "#dc3545",

            cancelButtonColor: "#6c757d",

            confirmButtonText: "Sí, eliminar",

            cancelButtonText: "Cancelar"

        }).then((result) => {

            if (result.isConfirmed) {

                window.location.href = url;

            }

        });

    });

});
