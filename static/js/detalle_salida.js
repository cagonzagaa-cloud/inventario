document.addEventListener(
"DOMContentLoaded",
function(){


// =====================================
// CARGAR PRECIO AUTOMÁTICO DEL PRODUCTO
// =====================================


const producto =
document.getElementById(
    "id_producto"
);


if(producto){


    producto.addEventListener(
    "change",
    function(){


        const id = this.value;



        if(id){


            fetch(
                `/salidas/producto/${id}/precio/`
            )


            .then(
                response => response.json()
            )


            .then(
                data => {


                    const precio =
                    document.getElementById(
                        "id_precio"
                    );


                    const cantidad =
                    document.getElementById(
                        "id_cantidad"
                    );



                    if(precio){

                        precio.value =
                        Number(data.precio)
                        .toFixed(2);

                    }



                    if(cantidad){

                        cantidad.max =
                        data.stock;

                    }


                }
            );


        }


    });


}






// =====================================
// ELIMINAR DETALLE DE SALIDA
// =====================================



const botonesEliminarDetalle =
document.querySelectorAll(
    ".btnEliminarDetalle"
);



botonesEliminarDetalle.forEach(
boton => {



    boton.addEventListener(
    "click",
    function(){



        const id =
        this.dataset.id;



        const producto =
        this.dataset.producto;



        const nombre =
        document.getElementById(
            "productoEliminarDetalle"
        );



        if(nombre){


            nombre.textContent =
            producto;


        }




        const formulario =
        document.getElementById(
            "formEliminarDetalle"
        );



        if(formulario){


            formulario.action =
            `/salidas/detalle/eliminar/${id}/`;


        }
    });



});

});