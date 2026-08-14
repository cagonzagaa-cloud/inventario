console.log("Sistema de Inventario iniciado");

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