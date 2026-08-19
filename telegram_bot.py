import os
import django

from decimal import Decimal, InvalidOperation
from asgiref.sync import sync_to_async


# ============================================================
# CONFIGURACIÓN DE DJANGO
# ============================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()


# ============================================================
# DJANGO
# ============================================================

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db import transaction


# ============================================================
# MODELOS
# ============================================================

from usuarios.models import PerfilUsuario
from configuracion.models import ConfiguracionSistema
from productos.models import Producto
from proveedores.models import Proveedor
from clientes.models import Cliente
from telegram_bot.models import SuscripcionTelegram
from telegram_bot.services import registrar_entrada_desde_bot, registrar_salida_desde_bot


User = get_user_model()


@sync_to_async
def vincular_chat(usuario, chat_id):
    SuscripcionTelegram.objects.update_or_create(
        usuario=usuario,
        defaults={"chat_id": chat_id, "activo": True},
    )


# ============================================================
# TELEGRAM
# ============================================================

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAX_PRODUCTOS = 10
MAX_PROVEEDORES = 20


# ============================================================
# UTILIDADES
# ============================================================

def limpiar_entrada(context):

    claves = [
        "entrada_estado",
        "entrada_proveedor_id",
        "entrada_proveedor_nombre",
        "entrada_producto_id",
        "entrada_producto_nombre",
        "entrada_producto_codigo",
        "entrada_cantidad",
        "entrada_costo",
    ]

    for clave in claves:
        context.user_data.pop(clave, None)


def boton_volver():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Volver al menú",
                callback_data="menu"
            )
        ]
    ])


# ============================================================
# MENÚ DE LOGIN
# ============================================================

def menu_login():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔐 Iniciar sesión",
                callback_data="login"
            )
        ]
    ])


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu_principal():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📦 Productos",
                callback_data="productos"
            ),
            InlineKeyboardButton(
                "📊 Stock",
                callback_data="stock"
            ),
        ],

        [
            InlineKeyboardButton(
                "⚠️ Stock bajo",
                callback_data="stock_bajo"
            ),
            InlineKeyboardButton(
                "🔎 Buscar producto",
                callback_data="buscar"
            ),
        ],

        [
            InlineKeyboardButton(
                "➕ Entrada",
                callback_data="entrada"
            ),
            InlineKeyboardButton(
                "➖ Salida",
                callback_data="salida"
            ),
        ],

        [InlineKeyboardButton("👥 Administración", callback_data="admin")],

        [
            InlineKeyboardButton(
                "🚪 Cerrar sesión",
                callback_data="logout"
            )
        ]

    ])


# ============================================================
# AUTENTICACIÓN
# ============================================================

@sync_to_async
def autenticar_usuario(username, password):

    return authenticate(
        username=username,
        password=password
    )


@sync_to_async
def obtener_perfil(usuario):

    try:
        return usuario.perfil

    except PerfilUsuario.DoesNotExist:
        return None


# ============================================================
# PROVEEDORES
# ============================================================

@sync_to_async
def obtener_proveedores():

    return list(
        Proveedor.objects
        .order_by("razon_social")[:MAX_PROVEEDORES]
    )


@sync_to_async
def obtener_proveedor(proveedor_id):

    return Proveedor.objects.get(
        id=proveedor_id
    )


# ============================================================
# PRODUCTOS
# ============================================================

@sync_to_async
def obtener_productos():

    return list(
        Producto.objects
        .filter(estado=True)
        .order_by("nombre")[:MAX_PRODUCTOS]
    )


@sync_to_async
def obtener_producto(producto_id):

    return Producto.objects.get(
        id=producto_id,
        estado=True
    )


# ============================================================
# START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if context.user_data.get("autenticado"):

        username = context.user_data.get(
            "username",
            "usuario"
        )

        await update.message.reply_text(

            f"🤖 *SISTEMA DE INVENTARIO*\n\n"
            f"Bienvenido nuevamente, *{username}*.\n\n"
            f"Selecciona una opción:",

            parse_mode="Markdown",

            reply_markup=menu_principal()
        )

        return

    await update.message.reply_text(

        "🤖 *SISTEMA DE INVENTARIO*\n\n"
        "Para utilizar el sistema debes iniciar sesión.",

        parse_mode="Markdown",

        reply_markup=menu_login()
    )


# ============================================================
# LOGIN
# ============================================================

async def iniciar_login(
    query,
    context
):

    context.user_data.clear()

    context.user_data["estado_login"] = "usuario"

    await query.edit_message_text(

        "🔐 *INICIO DE SESIÓN*\n\n"
        "Ingresa tu nombre de usuario:",

        parse_mode="Markdown"
    )


async def procesar_login(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    estado = context.user_data.get(
        "estado_login"
    )

    texto = update.message.text.strip()


    # --------------------------------------------------------
    # USUARIO
    # --------------------------------------------------------

    if estado == "usuario":

        context.user_data[
            "login_username"
        ] = texto

        context.user_data[
            "estado_login"
        ] = "password"

        await update.message.reply_text(

            "🔑 *CONTRASEÑA*\n\n"
            "Ingresa tu contraseña:",

            parse_mode="Markdown"
        )

        return


    # --------------------------------------------------------
    # CONTRASEÑA
    # --------------------------------------------------------

    if estado == "password":

        username = context.user_data.get(
            "login_username"
        )

        password = texto

        usuario = await autenticar_usuario(
            username,
            password
        )

        if usuario is None:

            context.user_data.clear()

            await update.message.reply_text(

                "❌ *INICIO DE SESIÓN FALLIDO*\n\n"
                "El usuario o la contraseña son incorrectos.",

                parse_mode="Markdown",

                reply_markup=menu_login()
            )

            return


        if not usuario.is_active:

            context.user_data.clear()

            await update.message.reply_text(

                "🚫 *USUARIO INACTIVO*\n\n"
                "Tu cuenta no está habilitada.",

                parse_mode="Markdown",

                reply_markup=menu_login()
            )

            return


        perfil = await obtener_perfil(
            usuario
        )

        es_admin = usuario.is_superuser or bool(perfil and perfil.es_administrador)

        if not es_admin:
            context.user_data.clear()
            await update.message.reply_text(
                "🚫 *ACCESO DENEGADO*\n\nEl bot está disponible únicamente para administradores.",
                parse_mode="Markdown",
                reply_markup=menu_login(),
            )
            return


        # ----------------------------------------------------
        # GUARDAR SESIÓN
        # ----------------------------------------------------

        context.user_data["autenticado"] = True

        context.user_data["usuario_id"] = usuario.id

        context.user_data["username"] = usuario.username

        context.user_data["es_admin"] = es_admin

        await vincular_chat(usuario, update.effective_chat.id)

        context.user_data.pop(
            "login_username",
            None
        )

        context.user_data.pop(
            "estado_login",
            None
        )


        rol = (
            "Administrador"
            if es_admin
            else
            "Usuario"
        )


        await update.message.reply_text(

            f"✅ *INICIO DE SESIÓN EXITOSO*\n\n"
            f"👤 Usuario: *{usuario.username}*\n"
            f"🔐 Rol: *{rol}*\n\n"
            f"Bienvenido al Sistema de Inventario.",

            parse_mode="Markdown",

            reply_markup=menu_principal()
        )


# ============================================================
# MOSTRAR MENÚ
# ============================================================

async def mostrar_menu(query):

    await query.edit_message_text(

        "🤖 *SISTEMA DE INVENTARIO*\n\n"
        "Selecciona una opción:",

        parse_mode="Markdown",

        reply_markup=menu_principal()
    )


# ============================================================
# PRODUCTOS
# ============================================================

async def mostrar_productos(query):

    productos = await obtener_productos()

    if not productos:

        await query.edit_message_text(

            "📦 *PRODUCTOS*\n\n"
            "No existen productos registrados.",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    mensaje = "📦 *PRODUCTOS REGISTRADOS*\n\n"


    for producto in productos:

        mensaje += (

            f"🔹 *{producto.nombre}*\n"
            f"   Código: `{producto.codigo}`\n"
            f"   Precio: ${producto.precio}\n"
            f"   Stock: {producto.stock}\n\n"

        )


    await query.edit_message_text(

        mensaje,

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


# ============================================================
# STOCK
# ============================================================

async def mostrar_stock(query):

    productos = await obtener_productos()

    if not productos:

        await query.edit_message_text(

            "📊 *STOCK*\n\n"
            "No existen productos registrados.",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    mensaje = "📊 *STOCK ACTUAL*\n\n"


    for producto in productos:

        if producto.esta_bajo_stock:

            estado = "⚠️ STOCK BAJO"

        else:

            estado = "✅ STOCK NORMAL"


        mensaje += (

            f"🔹 *{producto.nombre}*\n"
            f"   Código: `{producto.codigo}`\n"
            f"   Stock: *{producto.stock}*\n"
            f"   Stock mínimo: {producto.stock_minimo}\n"
            f"   {estado}\n\n"

        )


    await query.edit_message_text(

        mensaje,

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


# ============================================================
# STOCK BAJO
# ============================================================

@sync_to_async
def obtener_productos_stock_bajo():

    productos = list(
        Producto.objects
        .filter(estado=True)
        .order_by("nombre")
    )

    return [
        producto
        for producto in productos
        if producto.esta_bajo_stock
    ]


async def mostrar_stock_bajo(query):

    productos = await obtener_productos_stock_bajo()

    if not productos:

        await query.edit_message_text(

            "✅ *STOCK BAJO*\n\n"
            "No existen productos con stock bajo.",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    mensaje = (
        "⚠️ *PRODUCTOS CON STOCK BAJO*\n\n"
    )


    for producto in productos[:MAX_PRODUCTOS]:

        mensaje += (

            f"🔴 *{producto.nombre}*\n"
            f"   Código: `{producto.codigo}`\n"
            f"   Stock actual: *{producto.stock}*\n"
            f"   Stock mínimo: {producto.stock_minimo}\n\n"

        )


    await query.edit_message_text(

        mensaje,

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


# ============================================================
# BÚSQUEDA
# ============================================================

async def iniciar_busqueda(
    query,
    context
):

    context.user_data[
        "esperando_busqueda"
    ] = True

    await query.edit_message_text(

        "🔎 *BUSCAR PRODUCTO*\n\n"
        "Escribe el nombre o código del producto.\n\n"
        "También puedes pulsar el botón para volver al menú.",

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


@sync_to_async
def buscar_productos(texto):

    productos = list(

        Producto.objects.filter(
            estado=True,
            nombre__icontains=texto
        ).order_by("nombre")[:MAX_PRODUCTOS]

    )


    if not productos:

        productos = list(

            Producto.objects.filter(
                estado=True,
                codigo__icontains=texto
            ).order_by("nombre")[:MAX_PRODUCTOS]

        )


    return productos


async def procesar_busqueda(
    update,
    context
):

    texto = update.message.text.strip()

    context.user_data[
        "esperando_busqueda"
    ] = False


    productos = await buscar_productos(
        texto
    )


    if not productos:

        await update.message.reply_text(

            "🔎 *BÚSQUEDA*\n\n"
            f"No encontré productos relacionados con:\n"
            f"`{texto}`",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    mensaje = (
        f"🔎 *RESULTADOS PARA:* `{texto}`\n\n"
    )


    for producto in productos:

        estado = (

            "⚠️ STOCK BAJO"
            if producto.esta_bajo_stock
            else
            "✅ STOCK NORMAL"

        )


        mensaje += (

            f"🔹 *{producto.nombre}*\n"
            f"   Código: `{producto.codigo}`\n"
            f"   Precio: ${producto.precio}\n"
            f"   Stock: {producto.stock}\n"
            f"   {estado}\n\n"

        )


    await update.message.reply_text(

        mensaje,

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


# ============================================================
# ENTRADAS
# ============================================================

def menu_proveedores(proveedores):

    keyboard = []


    for proveedor in proveedores:

        keyboard.append([

            InlineKeyboardButton(

                proveedor.razon_social,

                callback_data=(
                    f"entrada_proveedor_{proveedor.id}"
                )

            )

        ])


    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Volver al menú",
            callback_data="menu"
        )

    ])


    return InlineKeyboardMarkup(
        keyboard
    )


def menu_productos_entrada(productos):

    keyboard = []


    for producto in productos:

        keyboard.append([

            InlineKeyboardButton(

                f"{producto.nombre} | Stock: {producto.stock}",

                callback_data=(
                    f"entrada_producto_{producto.id}"
                )

            )

        ])


    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Volver al menú",
            callback_data="menu"
        )

    ])


    return InlineKeyboardMarkup(
        keyboard
    )


# ============================================================
# INICIAR ENTRADA
# ============================================================

async def mostrar_entrada(
    query,
    context
):

    proveedores = await obtener_proveedores()


    if not proveedores:

        await query.edit_message_text(

            "➕ *REGISTRAR ENTRADA*\n\n"
            "❌ No existen proveedores registrados.",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    context.user_data[
        "entrada_estado"
    ] = "proveedor"


    await query.edit_message_text(

        "➕ *NUEVA ENTRADA*\n\n"
        "Selecciona el proveedor:",

        parse_mode="Markdown",

        reply_markup=menu_proveedores(
            proveedores
        )
    )


# ============================================================
# SELECCIONAR PROVEEDOR
# ============================================================

async def seleccionar_proveedor(
    query,
    context,
    proveedor_id
):

    try:

        proveedor = await obtener_proveedor(
            proveedor_id
        )

    except Proveedor.DoesNotExist:

        await query.edit_message_text(

            "❌ El proveedor ya no existe.",

            reply_markup=boton_volver()
        )

        return


    context.user_data[
        "entrada_proveedor_id"
    ] = proveedor.id

    context.user_data[
        "entrada_proveedor_nombre"
    ] = proveedor.razon_social


    productos = await obtener_productos()


    if not productos:

        await query.edit_message_text(

            "❌ No existen productos activos.",

            reply_markup=boton_volver()
        )

        return


    context.user_data[
        "entrada_estado"
    ] = "producto"


    await query.edit_message_text(

        f"➕ *NUEVA ENTRADA*\n\n"
        f"🏢 Proveedor:\n"
        f"*{proveedor.razon_social}*\n\n"
        f"📦 Selecciona el producto:",

        parse_mode="Markdown",

        reply_markup=menu_productos_entrada(
            productos
        )
    )


# ============================================================
# SELECCIONAR PRODUCTO
# ============================================================

async def seleccionar_producto_entrada(
    query,
    context,
    producto_id
):

    try:

        producto = await obtener_producto(
            producto_id
        )

    except Producto.DoesNotExist:

        await query.edit_message_text(

            "❌ El producto no existe o está inactivo.",

            reply_markup=boton_volver()
        )

        return


    context.user_data[
        "entrada_producto_id"
    ] = producto.id

    context.user_data[
        "entrada_producto_nombre"
    ] = producto.nombre

    context.user_data[
        "entrada_producto_codigo"
    ] = producto.codigo

    context.user_data[
        "entrada_estado"
    ] = "cantidad"


    await query.edit_message_text(

        f"📦 *PRODUCTO SELECCIONADO*\n\n"
        f"Producto: *{producto.nombre}*\n"
        f"Código: `{producto.codigo}`\n"
        f"Stock actual: *{producto.stock}*\n\n"
        f"✏️ Escribe la cantidad que ingresará.\n\n"
        f"💡 Si elegiste el producto incorrecto, "
        f"pulsa *⬅️ Volver al menú*.",

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


# ============================================================
# CANTIDAD
# ============================================================

async def procesar_cantidad_entrada(
    update,
    context
):

    texto = update.message.text.strip()


    try:

        cantidad = int(texto)

    except ValueError:

        await update.message.reply_text(

            "❌ La cantidad debe ser un número entero.\n\n"
            "Ejemplo: `10`",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    if cantidad <= 0:

        await update.message.reply_text(

            "❌ La cantidad debe ser mayor que cero.",

            reply_markup=boton_volver()
        )

        return


    context.user_data[
        "entrada_cantidad"
    ] = cantidad

    context.user_data[
        "entrada_estado"
    ] = "costo"


    await update.message.reply_text(

        "💰 *COSTO UNITARIO*\n\n"
        "Ingresa el costo unitario.\n\n"
        "Ejemplo:\n"
        "`12.50`\n\n"
        "💡 Si deseas cancelar la operación, "
        "pulsa *⬅️ Volver al menú*.",

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


# ============================================================
# COSTO
# ============================================================

async def procesar_costo_entrada(
    update,
    context
):

    texto = (
        update.message.text
        .strip()
        .replace(",", ".")
    )


    try:

        costo = Decimal(texto)

    except InvalidOperation:

        await update.message.reply_text(

            "❌ Ingresa un costo válido.\n\n"
            "Ejemplo: `12.50`",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    if costo < 0:

        await update.message.reply_text(

            "❌ El costo no puede ser negativo.",

            reply_markup=boton_volver()
        )

        return


    costo = costo.quantize(
        Decimal("0.01")
    )


    context.user_data[
        "entrada_costo"
    ] = costo

    context.user_data[
        "entrada_estado"
    ] = "confirmar"


    cantidad = context.user_data[
        "entrada_cantidad"
    ]

    nombre = context.user_data[
        "entrada_producto_nombre"
    ]

    proveedor = context.user_data[
        "entrada_proveedor_nombre"
    ]


    subtotal = (
        costo * Decimal(cantidad)
    )


    await update.message.reply_text(

        f"📋 *RESUMEN DE ENTRADA*\n\n"

        f"🏢 Proveedor:\n"
        f"*{proveedor}*\n\n"

        f"📦 Producto:\n"
        f"*{nombre}*\n\n"

        f"🔢 Cantidad:\n"
        f"*{cantidad}*\n\n"

        f"💰 Costo unitario:\n"
        f"*${costo:.2f}*\n\n"

        f"💵 Costo base:\n"
        f"*${subtotal:.2f}*\n\n"

        f"¿Deseas registrar esta entrada?",

        parse_mode="Markdown",

        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "✅ Confirmar entrada",
                    callback_data="confirmar_entrada"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔄 Elegir otro producto",
                    callback_data="cambiar_producto"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ Volver al menú",
                    callback_data="menu"
                )
            ]

        ])
    )


# ============================================================
# CAMBIAR PRODUCTO
# ============================================================

async def cambiar_producto_entrada(
    query,
    context
):

    proveedor_nombre = context.user_data.get(
        "entrada_proveedor_nombre"
    )


    # Mantener proveedor.
    # Limpiar información del producto.

    claves = [

        "entrada_producto_id",
        "entrada_producto_nombre",
        "entrada_producto_codigo",
        "entrada_cantidad",
        "entrada_costo",
        "entrada_estado",

    ]


    for clave in claves:

        context.user_data.pop(
            clave,
            None
        )


    productos = await obtener_productos()


    if not productos:

        await query.edit_message_text(

            "❌ No existen productos activos.",

            reply_markup=boton_volver()
        )

        return


    context.user_data[
        "entrada_estado"
    ] = "producto"


    await query.edit_message_text(

        f"🔄 *CAMBIAR PRODUCTO*\n\n"
        f"🏢 Proveedor:\n"
        f"*{proveedor_nombre}*\n\n"
        f"📦 Selecciona nuevamente el producto:",

        parse_mode="Markdown",

        reply_markup=menu_productos_entrada(
            productos
        )
    )


# ============================================================
# CREAR ENTRADA
# ============================================================

@sync_to_async
def crear_entrada(
    usuario_id,
    proveedor_id,
    producto_id,
    cantidad,
    costo
):

    return registrar_entrada_desde_bot(
        usuario_id, proveedor_id, producto_id, cantidad, costo
    )


# ============================================================
# CONFIRMAR ENTRADA
# ============================================================

async def confirmar_entrada(
    query,
    context
):

    usuario_id = context.user_data.get(
        "usuario_id"
    )

    proveedor_id = context.user_data.get(
        "entrada_proveedor_id"
    )

    producto_id = context.user_data.get(
        "entrada_producto_id"
    )

    cantidad = context.user_data.get(
        "entrada_cantidad"
    )

    costo = context.user_data.get(
        "entrada_costo"
    )


    if not all([

        usuario_id,
        proveedor_id,
        producto_id,
        cantidad,
        costo is not None

    ]):

        await query.edit_message_text(

            "❌ *ERROR*\n\n"
            "La información de la entrada está incompleta.",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    try:

        (
            entrada,
            producto,
            stock_anterior

        ) = await crear_entrada(

            usuario_id,

            proveedor_id,

            producto_id,

            cantidad,

            costo

        )


    except Exception as e:

        print(
            f"❌ ERROR AL CREAR ENTRADA: {e}"
        )

        await query.edit_message_text(

            "❌ *ERROR AL REGISTRAR LA ENTRADA*\n\n"
            "No fue posible completar la operación.\n\n"
            "Revisa la consola para conocer el error.",

            parse_mode="Markdown",

            reply_markup=boton_volver()
        )

        return


    stock_nuevo = producto.stock


    limpiar_entrada(context)


    await query.edit_message_text(

        f"✅ *ENTRADA REGISTRADA CORRECTAMENTE*\n\n"

        f"📋 Código: `{entrada.codigo}`\n"
        f"📦 Producto: *{producto.nombre}*\n\n"

        f"📊 Stock anterior: {stock_anterior}\n"
        f"➕ Entrada: +{cantidad}\n"
        f"📊 Stock nuevo: *{stock_nuevo}*\n\n"

        f"💰 Costo unitario: ${costo:.2f}\n"
        f"💵 Total: ${entrada.total:.2f}\n\n"

        f"🟢 Estado: CONFIRMADA",

        parse_mode="Markdown",

        reply_markup=menu_principal()
    )


# ============================================================
# CANCELAR ENTRADA
# ============================================================

async def cancelar_entrada(
    query,
    context
):

    limpiar_entrada(context)


    await query.edit_message_text(

        "❌ *ENTRADA CANCELADA*\n\n"
        "No se realizaron cambios en el inventario.",

        parse_mode="Markdown",

        reply_markup=menu_principal()
    )


# ============================================================
# SALIDAS
# ============================================================

async def mostrar_salida(query):

    await query.edit_message_text(

        "➖ *SALIDAS*\n\n"
        "El módulo de salidas será conectado en el siguiente paso.",

        parse_mode="Markdown",

        reply_markup=boton_volver()
    )


# ============================================================
# REPORTES
# ============================================================

def limpiar_salida(context):
    for clave in ["salida_estado", "salida_cliente_id", "salida_producto_id"]:
        context.user_data.pop(clave, None)


@sync_to_async
def obtener_clientes():
    return list(Cliente.objects.filter(estado=True).order_by("apellidos", "nombres")[:20])


async def mostrar_salida(query, context=None):
    if context:
        limpiar_salida(context)
    clientes = await obtener_clientes()
    if not clientes:
        await query.edit_message_text("No existen clientes activos. Registra uno en el sistema web.", reply_markup=boton_volver())
        return
    teclado = [[InlineKeyboardButton(c.nombre_completo, callback_data=f"salida_cliente_{c.pk}")] for c in clientes]
    teclado.append([InlineKeyboardButton("Volver", callback_data="menu")])
    await query.edit_message_text("*NUEVA SALIDA - PASO 1/3*\n\nSelecciona el cliente:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))


async def seleccionar_cliente_salida(query, context, cliente_id):
    context.user_data["salida_cliente_id"] = cliente_id
    productos = await obtener_productos()
    teclado = [[InlineKeyboardButton(f"{p.nombre} (stock {p.stock})", callback_data=f"salida_producto_{p.pk}")] for p in productos if p.stock > 0]
    teclado.append([InlineKeyboardButton("Cancelar", callback_data="menu")])
    await query.edit_message_text("*NUEVA SALIDA - PASO 2/3*\n\nSelecciona el producto:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))


async def seleccionar_producto_salida(query, context, producto_id):
    producto = await obtener_producto(producto_id)
    context.user_data["salida_producto_id"] = producto.pk
    context.user_data["salida_estado"] = "cantidad"
    await query.edit_message_text(
        f"*NUEVA SALIDA - PASO 3/3*\n\nProducto: *{producto.nombre}*\nDisponible: *{producto.stock}*\nPrecio: *${producto.precio}*\n\nEscribe la cantidad:",
        parse_mode="Markdown", reply_markup=boton_volver())


@sync_to_async
def crear_salida_bot(usuario_id, cliente_id, producto_id, cantidad):
    salida = registrar_salida_desde_bot(usuario_id, cliente_id, producto_id, cantidad)
    return salida.codigo, salida.total

async def procesar_cantidad_salida(update, context):
    try:
        cantidad = int(update.message.text.strip())
        codigo, total = await crear_salida_bot(
            context.user_data["usuario_id"], context.user_data["salida_cliente_id"],
            context.user_data["salida_producto_id"], cantidad)
    except (ValueError, KeyError) as exc:
        await update.message.reply_text(f"Error: {exc}\nIngresa una cantidad válida o vuelve al menú.", reply_markup=boton_volver())
        return
    limpiar_salida(context)
    await update.message.reply_text(f"Salida *{codigo}* confirmada.\nTotal: *${total}*", parse_mode="Markdown", reply_markup=menu_principal())


# ============================================================
# ADMINISTRACIÓN
# ============================================================

def menu_administracion():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Usuarios", callback_data="admin_usuarios")],
        [InlineKeyboardButton("⚙️ Configuración", callback_data="admin_configuracion")],
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="menu")],
    ])


@sync_to_async
def obtener_usuarios_admin():
    return list(User.objects.select_related("perfil").order_by("username")[:30])


@sync_to_async
def obtener_configuracion_admin():
    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    return configuracion


def _validar_actor_admin(actor):
    perfil = getattr(actor, "perfil", None)
    if not (actor.is_active and (actor.is_superuser or (perfil and perfil.es_administrador))):
        raise PermissionError("Ya no tienes permisos de administrador.")


@sync_to_async
@transaction.atomic
def alternar_estado_usuario(actor_id, usuario_id):
    actor = User.objects.select_related("perfil").get(pk=actor_id)
    _validar_actor_admin(actor)
    usuario = User.objects.select_for_update().get(pk=usuario_id)
    if usuario.pk == actor.pk:
        raise ValueError("No puedes desactivar tu propia cuenta.")
    if usuario.is_superuser and not actor.is_superuser:
        raise PermissionError("Solo otro superusuario puede cambiar ese estado.")
    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])
    return usuario.username, usuario.is_active


@sync_to_async
@transaction.atomic
def alternar_rol_usuario(actor_id, usuario_id):
    actor = User.objects.select_related("perfil").get(pk=actor_id)
    _validar_actor_admin(actor)
    usuario = User.objects.select_related("perfil").select_for_update().get(pk=usuario_id)
    if usuario.pk == actor.pk:
        raise ValueError("No puedes cambiar tu propio rol.")
    if usuario.is_superuser:
        raise ValueError("No se puede cambiar el rol de un superusuario.")
    usuario.perfil.rol = (
        PerfilUsuario.Rol.USUARIO
        if usuario.perfil.es_administrador
        else PerfilUsuario.Rol.ADMIN
    )
    usuario.perfil.save(update_fields=["rol"])
    return usuario.username, usuario.perfil.get_rol_display()


async def mostrar_admin(query, context):
    if not context.user_data.get("es_admin"):
        await query.edit_message_text("🚫 Acceso denegado.", reply_markup=boton_volver())
        return
    await query.edit_message_text(
        "👥 *ADMINISTRACIÓN*\n\nGestiona usuarios o consulta la configuración del sistema.",
        parse_mode="Markdown", reply_markup=menu_administracion(),
    )


async def mostrar_usuarios_admin(query):
    usuarios = await obtener_usuarios_admin()
    teclado = []
    for usuario in usuarios:
        estado = "✅" if usuario.is_active else "⛔"
        rol = "Admin" if usuario.is_superuser or usuario.perfil.es_administrador else "Usuario"
        teclado.append([InlineKeyboardButton(
            f"{estado} {usuario.username} · {rol}", callback_data=f"admin_usuario_{usuario.pk}"
        )])
    teclado.append([InlineKeyboardButton("⬅️ Administración", callback_data="admin")])
    await query.edit_message_text(
        "👥 *USUARIOS*\n\nSelecciona un usuario para administrar su estado y rol.",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado),
    )


async def mostrar_usuario_admin(query, usuario_id):
    usuarios = await obtener_usuarios_admin()
    usuario = next((item for item in usuarios if item.pk == usuario_id), None)
    if not usuario:
        await query.edit_message_text("El usuario ya no existe.", reply_markup=menu_administracion())
        return
    rol = "Administrador" if usuario.is_superuser or usuario.perfil.es_administrador else "Usuario"
    estado = "Activo" if usuario.is_active else "Inactivo"
    teclado = [
        [InlineKeyboardButton("🔄 Activar / desactivar", callback_data=f"admin_estado_{usuario.pk}")],
    ]
    if not usuario.is_superuser:
        teclado.append([InlineKeyboardButton("🔐 Cambiar rol", callback_data=f"admin_rol_{usuario.pk}")])
    teclado.append([InlineKeyboardButton("⬅️ Usuarios", callback_data="admin_usuarios")])
    await query.edit_message_text(
        f"👤 *{usuario.username}*\n\nNombre: {usuario.get_full_name() or '-'}\nCorreo: {usuario.email or '-'}\nRol: *{rol}*\nEstado: *{estado}*",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado),
    )


async def mostrar_configuracion_admin(query):
    config = await obtener_configuracion_admin()
    await query.edit_message_text(
        f"⚙️ *CONFIGURACIÓN DEL SISTEMA*\n\nEmpresa: *{config.nombre_empresa}*\nRUC/RIF: {config.rif or '-'}\nCorreo: {config.correo or '-'}\nTeléfono: {config.telefono or '-'}\nMoneda: {config.moneda}\nIVA configurado: {config.impuesto_iva}%\nAlerta de stock: {config.stock_minimo_alerta}\nHorario: {config.horario_atencion or '-'}",
        parse_mode="Markdown", reply_markup=menu_administracion(),
    )


# ============================================================
# CERRAR SESIÓN
# ============================================================

async def cerrar_sesion(
    query,
    context
):

    context.user_data.clear()


    await query.edit_message_text(

        "🚪 *SESIÓN CERRADA*\n\n"
        "Tu sesión se cerró correctamente.",

        parse_mode="Markdown",

        reply_markup=menu_login()
    )


# ============================================================
# VOLVER AL MENÚ DESDE TEXTO
# ============================================================

async def volver_al_menu_desde_texto(
    update,
    context
):

    texto = (
        update.message.text
        .strip()
        .lower()
    )


    if texto not in [
        "volver",
        "menu",
        "menú",
        "cancelar"
    ]:

        return False


    # Si estaba en login, cancelar login

    if context.user_data.get(
        "estado_login"
    ):

        context.user_data.clear()

        await update.message.reply_text(

            "❌ *INICIO DE SESIÓN CANCELADO*\n\n"
            "Puedes volver a iniciar sesión cuando quieras.",

            parse_mode="Markdown",

            reply_markup=menu_login()
        )

        return True


    # Limpiar búsqueda

    context.user_data.pop(
        "esperando_busqueda",
        None
    )


    # Limpiar entrada

    limpiar_entrada(
        context
    )


    # Si no está autenticado

    if not context.user_data.get(
        "autenticado"
    ):

        await update.message.reply_text(

            "🔐 Debes iniciar sesión primero.",

            reply_markup=menu_login()
        )

        return True


    await update.message.reply_text(

        "🏠 *MENÚ PRINCIPAL*\n\n"
        "Selecciona una opción:",

        parse_mode="Markdown",

        reply_markup=menu_principal()
    )


    return True


# ============================================================
# MANEJAR BOTONES
# ============================================================

async def manejar_boton(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    opcion = query.data


    # ========================================================
    # LOGIN
    # ========================================================

    if opcion == "login":

        await iniciar_login(
            query,
            context
        )

        return


    # ========================================================
    # LOGOUT
    # ========================================================

    if opcion == "logout":

        await cerrar_sesion(
            query,
            context
        )

        return


    # ========================================================
    # VERIFICAR LOGIN
    # ========================================================

    if not context.user_data.get(
        "autenticado"
    ):

        await query.edit_message_text(

            "🚫 *ACCESO DENEGADO*\n\n"
            "Debes iniciar sesión primero.",

            parse_mode="Markdown",

            reply_markup=menu_login()
        )

        return


    # ========================================================
    # MENÚ
    # ========================================================

    if opcion == "menu":

        limpiar_entrada(
            context
        )

        limpiar_salida(context)

        context.user_data.pop(
            "esperando_busqueda",
            None
        )

        await mostrar_menu(
            query
        )

        return


    # ========================================================
    # PRODUCTOS
    # ========================================================

    if opcion == "productos":

        await mostrar_productos(
            query
        )

        return


    # ========================================================
    # STOCK
    # ========================================================

    if opcion == "stock":

        await mostrar_stock(
            query
        )

        return


    # ========================================================
    # STOCK BAJO
    # ========================================================

    if opcion == "stock_bajo":

        await mostrar_stock_bajo(
            query
        )

        return


    # ========================================================
    # BÚSQUEDA
    # ========================================================

    if opcion == "buscar":

        await iniciar_busqueda(
            query,
            context
        )

        return


    # ========================================================
    # ENTRADA
    # ========================================================

    if opcion == "entrada":

        limpiar_entrada(
            context
        )

        await mostrar_entrada(
            query,
            context
        )

        return


    # ========================================================
    # PROVEEDOR
    # ========================================================

    if opcion.startswith(
        "entrada_proveedor_"
    ):

        proveedor_id = int(

            opcion.replace(
                "entrada_proveedor_",
                ""
            )

        )


        await seleccionar_proveedor(

            query,

            context,

            proveedor_id

        )

        return


    # ========================================================
    # PRODUCTO
    # ========================================================

    if opcion.startswith(
        "entrada_producto_"
    ):

        producto_id = int(

            opcion.replace(
                "entrada_producto_",
                ""
            )

        )


        await seleccionar_producto_entrada(

            query,

            context,

            producto_id

        )

        return


    # ========================================================
    # CAMBIAR PRODUCTO
    # ========================================================

    if opcion == "cambiar_producto":

        await cambiar_producto_entrada(

            query,

            context

        )

        return


    # ========================================================
    # CONFIRMAR
    # ========================================================

    if opcion == "confirmar_entrada":

        await confirmar_entrada(

            query,

            context

        )

        return


    # ========================================================
    # CANCELAR
    # ========================================================

    if opcion == "cancelar_entrada":

        await cancelar_entrada(

            query,

            context

        )

        return


    # ========================================================
    # SALIDA
    # ========================================================

    if opcion == "salida":

        await mostrar_salida(
            query,
            context
        )

        return

    if opcion.startswith("salida_cliente_"):
        await seleccionar_cliente_salida(query, context, int(opcion.replace("salida_cliente_", "")))
        return

    if opcion.startswith("salida_producto_"):
        await seleccionar_producto_salida(query, context, int(opcion.replace("salida_producto_", "")))
        return


    # ========================================================
    # ADMINISTRACIÓN
    # ========================================================

    if opcion == "admin":

        await mostrar_admin(

            query,

            context

        )

        return


    if opcion == "admin_usuarios":
        await mostrar_usuarios_admin(query)
        return

    if opcion == "admin_configuracion":
        await mostrar_configuracion_admin(query)
        return

    if opcion.startswith("admin_usuario_"):
        await mostrar_usuario_admin(query, int(opcion.replace("admin_usuario_", "")))
        return

    if opcion.startswith("admin_estado_"):
        usuario_id = int(opcion.replace("admin_estado_", ""))
        try:
            await alternar_estado_usuario(context.user_data["usuario_id"], usuario_id)
            await mostrar_usuario_admin(query, usuario_id)
        except (ValueError, PermissionError, KeyError) as exc:
            await query.edit_message_text(f"❌ {exc}", reply_markup=menu_administracion())
        return

    if opcion.startswith("admin_rol_"):
        usuario_id = int(opcion.replace("admin_rol_", ""))
        try:
            await alternar_rol_usuario(context.user_data["usuario_id"], usuario_id)
            await mostrar_usuario_admin(query, usuario_id)
        except (ValueError, PermissionError, KeyError) as exc:
            await query.edit_message_text(f"❌ {exc}", reply_markup=menu_administracion())
        return


# ============================================================
# MANEJAR MENSAJES DE TEXTO
# ============================================================

async def manejar_mensaje(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # ========================================================
    # VOLVER / CANCELAR
    # ========================================================

    if await volver_al_menu_desde_texto(

        update,

        context

    ):

        return


    # ========================================================
    # LOGIN
    # ========================================================

    if context.user_data.get(
        "estado_login"
    ):

        await procesar_login(

            update,

            context

        )

        return


    # ========================================================
    # NO AUTENTICADO
    # ========================================================

    if not context.user_data.get(
        "autenticado"
    ):

        await update.message.reply_text(

            "🔐 Debes iniciar sesión primero.",

            reply_markup=menu_login()
        )

        return


    # ========================================================
    # ENTRADA - CANTIDAD
    # ========================================================

    if context.user_data.get(
        "entrada_estado"
    ) == "cantidad":

        await procesar_cantidad_entrada(

            update,

            context

        )

        return


    # ========================================================
    # ENTRADA - COSTO
    # ========================================================

    if context.user_data.get(
        "entrada_estado"
    ) == "costo":

        await procesar_costo_entrada(

            update,

            context

        )

        return

    if context.user_data.get("salida_estado") == "cantidad":
        await procesar_cantidad_salida(update, context)
        return


    # ========================================================
    # BÚSQUEDA
    # ========================================================

    if context.user_data.get(
        "esperando_busqueda"
    ):

        await procesar_busqueda(

            update,

            context

        )

        return


    # ========================================================
    # TEXTO NORMAL
    # ========================================================

    await update.message.reply_text(

        "ℹ️ Utiliza los botones del menú.",

        reply_markup=menu_principal()
    )


# ============================================================
# MAIN
# ============================================================

def main():

    token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )


    if not token:

        print(
            "❌ No se encontró "
            "TELEGRAM_BOT_TOKEN"
        )

        return


    app = (

        Application
        .builder()
        .token(token)
        .build()

    )


    # ========================================================
    # START
    # ========================================================

    app.add_handler(

        CommandHandler(
            "start",
            start
        )

    )


    # ========================================================
    # BOTONES
    # ========================================================

    app.add_handler(

        CallbackQueryHandler(
            manejar_boton
        )

    )


    # ========================================================
    # MENSAJES
    # ========================================================

    app.add_handler(

        MessageHandler(

            filters.TEXT & ~filters.COMMAND,

            manejar_mensaje

        )

    )


    # ========================================================
    # INICIAR
    # ========================================================

    print(
        "🤖 Bot iniciado correctamente..."
    )

    print(
        "Esperando mensajes de Telegram..."
    )


    app.run_polling()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    main()
