document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");

    const main = document.querySelector(".main-content");

    const boton = document.getElementById("toggleSidebar");

    if(localStorage.getItem("sidebar") === "hide"){

        sidebar.classList.add("oculto");

        main.classList.add("expandido");

    }

    boton.addEventListener("click", function(){

        sidebar.classList.toggle("oculto");

        main.classList.toggle("expandido");

        if(sidebar.classList.contains("oculto")){

            localStorage.setItem("sidebar","hide");

        }else{

            localStorage.setItem("sidebar","show");

        }

    });

});