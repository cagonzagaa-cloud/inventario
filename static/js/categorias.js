$(document).ready(function () {

    //----------------------------------------
    // CONFIGURACIÓN
    //----------------------------------------

    const urlCrear = $('#formCategoria').attr('action');

    //----------------------------------------
    // DATATABLE
    //----------------------------------------

    $('#tablaCategorias').DataTable({

        responsive: true,

        pageLength: 5,

        lengthMenu: [5, 10, 20, 50],

        order: [[0, 'desc']],

        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json'
        }

    });

    //----------------------------------------
    // NUEVA CATEGORÍA
    //----------------------------------------

    function mostrarFormularioCategoria() {
        const panel = $('#categoriaFormPanel');
        panel.removeClass('d-none');
        panel[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
        $('#id_nombre').focus();
    }

    function ocultarFormularioCategoria() {
        $('#categoriaFormPanel').addClass('d-none');
    }

    $('#btnCerrarCategoria').on('click', function () {
        $('#formCategoria')[0].reset();
        ocultarFormularioCategoria();
    });

    $('#btnNuevaCategoria').click(function () {

        $('#tituloModal').text('Nueva Categoría');

        $('#formCategoria').attr('action', urlCrear);

        $('#id_nombre').val('');
        $('#id_descripcion').val('');
        $('#id_estado').prop('checked', true);

        limpiarErrores();
        mostrarFormularioCategoria();

    });

    //----------------------------------------
    // EDITAR CATEGORÍA
    //----------------------------------------
    $(document).on("click", ".btnEditar", function () {

        $("#tituloModal").text("Editar Categoría");
        mostrarFormularioCategoria();

        $("#formCategoria").attr("action", $(this).attr("data-url"));

        $("#id_nombre").val($(this).attr("data-nombre"));
        $("#id_descripcion").val($(this).attr("data-descripcion"));
        $("#id_estado").prop(
            "checked",
            $(this).attr("data-estado") === "True" ||
            $(this).attr("data-estado") === "true"
        );

    });

    //----------------------------------------
    // VALIDACIÓN
    //----------------------------------------

    $('#formCategoria').submit(function (e) {

        let nombre = $('#nombre').val().trim();

        let descripcion = $('#descripcion').val().trim();

        let valido = true;

        limpiarErrores();

        if (nombre.length < 3) {

            $('#id_nombre').addClass('is-invalid');

            $('#errorNombre').text(
                'El nombre debe tener al menos 3 caracteres.'
            );

            valido = false;

        }

        if (descripcion.length < 5) {

            $('#id_descripcion').addClass('is-invalid');

            $('#errorDescripcion').text(
                'La descripción debe tener al menos 5 caracteres.'
            );

            valido = false;

        }

        if (!valido) {

            e.preventDefault();

            Swal.fire({

                icon: 'warning',

                title: 'Formulario incompleto',

                text: 'Corrija los campos marcados antes de continuar.'

            });

            return;

        }

        ocultarFormularioCategoria();

    });

    //----------------------------------------
    // ELIMINAR
    //----------------------------------------

    $('.btnEliminar').click(function () {

        let url = $(this).data('url');

        let nombre = $(this).data('nombre');

        Swal.fire({

            title: '¿Eliminar categoría?',

            html: `Se eliminará la categoría <b>${nombre}</b>.`,

            icon: 'warning',

            showCancelButton: true,

            confirmButtonColor: '#dc3545',

            cancelButtonColor: '#6c757d',

            confirmButtonText: 'Sí, eliminar',

            cancelButtonText: 'Cancelar',

            reverseButtons: true

        }).then((result) => {

            if (result.isConfirmed) {

                window.location.href = url;

            }

        });

    });

    //----------------------------------------
    // LIMPIAR ERRORES
    //----------------------------------------

    function limpiarErrores() {

        $('#id_nombre').removeClass('is-invalid');
        $('#id_descripcion').removeClass('is-invalid');

        $('#errorNombre').text('');
        $('#errorDescripcion').text('');

    }

});