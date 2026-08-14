document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // EDITAR CLIENTE
    // ===============================

    document.querySelectorAll(".btnEditarCliente").forEach(function (boton) {

        boton.addEventListener("click", function () {

            document.getElementById("editar_tipo_identificacion").value = this.dataset.tipo;
            document.getElementById("editar_identificacion").value = this.dataset.identificacion;
            document.getElementById("editar_nombres").value = this.dataset.nombres;
            document.getElementById("editar_apellidos").value = this.dataset.apellidos;
            document.getElementById("editar_telefono").value = this.dataset.telefono || "";
            document.getElementById("editar_correo").value = this.dataset.correo || "";
            document.getElementById("editar_direccion").value = this.dataset.direccion || "";

            document.getElementById("editar_estado").checked =
                this.dataset.estado === "True";

            document.getElementById("formEditarCliente").action =
                "/clientes/editar/" + this.dataset.id + "/";

        });

    });

    // ===============================
    // ELIMINAR CLIENTE
    // ===============================

    document.querySelectorAll(".btnEliminarCliente").forEach(function (boton) {

        boton.addEventListener("click", function () {

            document.getElementById("nombreClienteEliminar").textContent =
                this.dataset.nombre;

            document.getElementById("formEliminarCliente").action =
                "/clientes/eliminar/" + this.dataset.id + "/";

        });

    });

});