$(document).ready(function () {

    // ==========================
    // DATATABLE
    // ==========================

    $('#tablaProveedores').DataTable({

        responsive: true,

        pageLength: 10,

        language: {

            url: 'https://cdn.datatables.net/plug-ins/2.3.2/i18n/es-ES.json'

        }

    });

    // ==========================
    // NUEVO PROVEEDOR
    // ==========================

    function mostrarFormularioProveedor() {
        const panel = $('#proveedorFormPanel');
        panel.removeClass('d-none');
        panel[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
        $('#id_codigo').focus();
    }

    function ocultarFormularioProveedor() {
        $('#proveedorFormPanel').addClass('d-none');
    }

    $('#btnNuevoProveedor').on('click', function () {

        $('#tituloProveedor').text("Nuevo Proveedor");

        $('#formProveedor').attr(
            "action",
            "/proveedores/nuevo/"
        );

        $('#formProveedor')[0].reset();
        mostrarFormularioProveedor();

    });

    $('#btnCerrarProveedor').on('click', function () {
        $('#formProveedor')[0].reset();
        ocultarFormularioProveedor();
    });

    // ==========================
    // EDITAR
    // ==========================

    $(document).on('click', '.btnEditar', function () {

        $('#tituloProveedor').text("Editar Proveedor");
        mostrarFormularioProveedor();

        $('#formProveedor').attr(
            "action",
            $(this).data("url")
        );

        $('#id_codigo').val($(this).data("codigo"));

        $('#id_tipo_identificacion').val($(this).data("tipo"));

        $('#id_identificacion').val($(this).data("identificacion"));

        $('#id_razon_social').val($(this).data("razonsocial"));

        $('#id_nombre_comercial').val($(this).data("comercial"));

        $('#id_contacto').val($(this).data("contacto"));

        $('#id_cargo').val($(this).data("cargo"));

        $('#id_telefono').val($(this).data("telefono"));

        $('#id_celular').val($(this).data("celular"));

        $('#id_correo').val($(this).data("correo"));

        $('#id_sitio_web').val($(this).data("web"));

        $('#id_direccion').val($(this).data("direccion"));

        $('#id_provincia').val($(this).data("provincia"));

        $('#id_canton').val($(this).data("canton"));

        $('#id_ciudad').val($(this).data("ciudad"));

        $('#id_codigo_postal').val($(this).data("postal"));

        $('#id_condicion_pago').val($(this).data("pago"));

        $('#id_cupo_credito').val($(this).data("cupo"));

        $('#id_observaciones').val($(this).data("observaciones"));

        $('#id_estado').prop(
            "checked",
            $(this).data("estado") === true ||
            $(this).data("estado") === "True" ||
            $(this).data("estado") === "true"
        );

    });

    // ==========================
    // VALIDACIONES
    // ==========================

    $('#formProveedor').submit(function (e) {

        let valido = true;

        $('#formProveedor .form-control, #formProveedor .form-select')
            .removeClass('is-invalid');

        $('#formProveedor .form-control, #formProveedor .form-select')
            .each(function () {

                if ($(this).prop("required")) {

                    if ($(this).val().trim() === "") {

                        $(this).addClass("is-invalid");

                        valido = false;

                    }

                }

            });

        if (!valido) {

            e.preventDefault();

            Swal.fire({

                icon: "warning",

                title: "Información incompleta",

                text: "Complete los campos obligatorios."

            });

            return;

        }

        ocultarFormularioProveedor();

    });

    // ==========================
    // ELIMINAR
    // ==========================

    $('.btnEliminar').click(function () {

        let url = $(this).data("url");

        let nombre = $(this).data("nombre");

        Swal.fire({

            title: "¿Eliminar proveedor?",

            html: `Se eliminará <b>${nombre}</b>.`,

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