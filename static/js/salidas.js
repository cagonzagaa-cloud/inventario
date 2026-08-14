document.addEventListener("DOMContentLoaded", function () {


    // ======================================
    // EDITAR SALIDA
    // ======================================

    const botonesEditar = document.querySelectorAll(".btnEditarSalida");


    botonesEditar.forEach(boton => {


        boton.addEventListener("click", function () {


            const id = this.dataset.id;



            // Cargar datos al formulario

            document.getElementById("editar_fecha").value =
                this.dataset.fecha;



            document.getElementById("editar_cliente").value =
                this.dataset.cliente;



            document.getElementById("editar_numero_documento").value =
                this.dataset.documento;



            document.getElementById("editar_tipo").value =
                this.dataset.tipo;



            document.getElementById("editar_estado").value =
                this.dataset.estado;



            document.getElementById("editar_observaciones").value =
                this.dataset.observaciones;



            // Cambiar acción del formulario

            document.getElementById("formEditarSalida").action =
                `/salidas/editar/${id}/`;


        });


    });





    // ======================================
    // ELIMINAR SALIDA
    // ======================================


    const botonesEliminar = document.querySelectorAll(".btnEliminarSalida");



    botonesEliminar.forEach(boton => {



        boton.addEventListener("click", function () {


            const id = this.dataset.id;



            const codigo = this.dataset.codigo;



            document.getElementById("codigoSalidaEliminar").textContent =
                codigo;



            document.getElementById("formEliminarSalida").action =
                `/salidas/eliminar/${id}/`;



        });



    });



});