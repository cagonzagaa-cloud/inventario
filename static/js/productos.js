$(document).ready(function () {

    //=========================================
    // DATATABLE
    //=========================================

    var tablaProductos = $('#tablaProductos').DataTable({

        responsive: true,

        pageLength: 10,

        lengthMenu: [5, 10, 20, 50],

        language: {

            url: 'https://cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json'

        }

    });

    $('#filtroTarifaIva').on('change', function () {
        var tarifa = $(this).val();
        tablaProductos.column(4).search(tarifa, false, false).draw();
    });


    //=========================================
    // NUEVO PRODUCTO
    //=========================================

    function mostrarFormularioProducto() {
        const panel = $('#productoFormPanel');
        panel.removeClass('d-none');
        panel[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
        $('#id_codigo').focus();
    }

    function ocultarFormularioProducto() {
        $('#productoFormPanel').addClass('d-none');
    }

    $('#btnCerrarProducto').on('click', function () {
        $('#formProducto')[0].reset();
        ocultarFormularioProducto();
    });

    $('#btnNuevoProducto').on('click', function () {

        $('#tituloProducto').text("Nuevo Producto");

        $('#formProducto').attr("action", "/productos/nuevo/");

        $('#formProducto')[0].reset();

        $('#id_estado').prop("checked", true);
        $('#id_clasificacion_tributaria').val('');

        $('.is-invalid').removeClass("is-invalid");
        mostrarFormularioProducto();

    });


    //=========================================
    // EDITAR PRODUCTO
    //=========================================

    $(document).on("click", ".btnEditarProducto", function () {

        $('#tituloProducto').text("Editar Producto");
        mostrarFormularioProducto();

        $('#formProducto').attr(
            "action",
            $(this).data("url")
        );

        $('#id_codigo').val($(this).data("codigo"));

        $('#id_nombre').val($(this).data("nombre"));

        $('#id_descripcion').val($(this).data("descripcion"));

        $('#id_categoria').val($(this).data("categoria"));
        $('#id_clasificacion_tributaria').val($(this).data("clasificacion"));

        let costo = $(this).attr("data-costo") || "0";
        let precio = $(this).attr("data-precio") || "0";

        costo = costo.replace(",", ".");
        precio = precio.replace(",", ".");

        $('#id_costo').val(costo);

        $('#id_precio').val(precio);

        $('#id_stock').val($(this).data("stock"));

        $('#id_stock_minimo').val($(this).data("stockminimo"));

        $('#id_estado').prop(

            "checked",

            $(this).data("estado") === true ||

            $(this).data("estado") === "True" ||

            $(this).data("estado") === "true"

        );

        $('.is-invalid').removeClass("is-invalid");

    });


    //=========================================
    // BLOQUEAR NÚMEROS NEGATIVOS
    //=========================================

    $('#id_costo, #id_precio, #id_stock, #id_stock_minimo').on(

        'keydown',

        function (e) {

            if (e.key === "-") {

                e.preventDefault();

            }

        }

    );


    //=========================================
    // VALIDACIONES
    //=========================================

    $('#formProducto').submit(function (e) {

        let valido = true;

        $('.is-invalid').removeClass("is-invalid");


        if ($('#id_codigo').val().trim() === "") {

            $('#id_codigo').addClass("is-invalid");

            valido = false;

        }


        if ($('#id_nombre').val().trim() === "") {

            $('#id_nombre').addClass("is-invalid");

            valido = false;

        }


        if ($('#id_categoria').val() === "") {

            $('#id_categoria').addClass("is-invalid");

            valido = false;

        }


        if (parseFloat($('#id_costo').val() || 0) < 0) {

            $('#id_costo').val(0);

            $('#id_costo').addClass("is-invalid");

            valido = false;

        }


        if (parseFloat($('#id_precio').val() || 0) < 0) {

            $('#id_precio').val(0);

            $('#id_precio').addClass("is-invalid");

            valido = false;

        }


        if (parseInt($('#id_stock').val() || 0) < 0) {

            $('#id_stock').val(0);

            $('#id_stock').addClass("is-invalid");

            valido = false;

        }


        if (parseInt($('#id_stock_minimo').val() || 0) < 0) {

            $('#id_stock_minimo').val(0);

            $('#id_stock_minimo').addClass("is-invalid");

            valido = false;

        }


        if (!valido) {

            e.preventDefault();

            Swal.fire({

                icon: "warning",

                title: "Datos inválidos",

                text: "Revise los campos marcados."

            });

            return;

        }

        ocultarFormularioProducto();

    });


    //=========================================
    // ELIMINAR PRODUCTO
    //=========================================

    $(document).on("click", ".btnEliminarProducto", function () {

        let url = $(this).data("url");

        let nombre = $(this).data("nombre");

        Swal.fire({

            title: "¿Eliminar producto?",

            html: `Se eliminará el producto <b>${nombre}</b>.`,

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