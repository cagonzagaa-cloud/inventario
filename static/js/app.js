console.log("Sistema de Inventario iniciado");

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btnAnularMovimiento").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const formulario = document.getElementById("formAnularMovimiento");
            const codigo = document.getElementById("codigoMovimientoAnular");
            const titulo = document.getElementById("modalAnularMovimientoLabel");

            if (formulario) formulario.action = this.dataset.url;
            if (codigo) codigo.textContent = this.dataset.codigo;
            if (titulo) {
                const tipo = this.dataset.tipo === "entrada" ? "entrada" : "salida";
                titulo.innerHTML = `<i class="bi bi-x-circle-fill me-2"></i> Anular ${tipo}`;
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {

    const logoutForm = document.getElementById("logoutForm");

    if (!logoutForm) return;

    logoutForm.addEventListener("submit", function (e) {

        e.preventDefault();

        Swal.fire({

            title: "¿Cerrar sesión?",

            text: "Se cerrará la sesión actual.",

            icon: "question",

            showCancelButton: true,

            confirmButtonText: "Sí, cerrar sesión",

            cancelButtonText: "Cancelar",

            confirmButtonColor: "#0d6efd",

            cancelButtonColor: "#dc3545"

        }).then((result) => {

            if (result.isConfirmed) {

                logoutForm.submit();

            }

        });

    });

});
