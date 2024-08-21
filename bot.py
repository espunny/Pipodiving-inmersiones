
# Versión con bases de datos.
# Versión multiclub Nuevos campos 'active_group' 'created_at'
# Versión que permitirá eliminar las inmersiones por fecha.
# Todos los mensajes se envían en modo silencioso.
# La base de datos estará en un servidor MariaDb.
import os
import aiomysql
import pymysql
import datetime
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import CommandHandler, CallbackQueryHandler, Filters, MessageHandler, Updater, ContextTypes
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application, MessageHandler, filters
from telegram.error import Forbidden


# Cargar variables de entorno desde el archivo .env
# load_dotenv()

# Variables del sistema
TOKEN = os.getenv('TOKEN')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
AUTHORIZED_GROUP_ID = os.getenv('AUTHORIZED_GROUP_ID')
AUTHORIZED_CHAT_ID = os.getenv('AUTHORIZED_CHAT_ID')

# Mensajes
BOT_NO_AUTORIZADO = 'Para autorizar este bot, escribe el comando /start y envía el identificador que aparece en un mensaje privado a: @t850model102'
NO_ADMINISTRADOR = 'Solamente un administrador del grupo puede usar este comando'

# Saber si un usuario es administrador
async def is_admin(user_id, chat_id, bot):
    chat_administrators = await bot.get_chat_administrators(chat_id)  # Await la coroutine
    for admin in chat_administrators:
        if admin.user.id == user_id:
            return True
    return False

# Conectar a la base de datos
def connect_db():
    return pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

# Verificación de autorización
def authorized(chat_id):
    # Convierte AUTHORIZED_GROUP_ID en una lista de IDs, eliminando espacios en blanco
    authorized_ids = [id.strip() for id in AUTHORIZED_GROUP_ID.split(',')]
    return str(chat_id) in authorized_ids

# Función de inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    await update.message.reply_text(f'El ID de tu grupo es {chat_id} y tu usuario es:{user_id} . {MYSQL_USER}')

# Comando /ver
async def ver(update: Update, context: ContextTypes.DEFAULT_TYPE, private=False):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        if update.message:
            await update.message.reply_text(BOT_NO_AUTORIZADO)
        elif update.callback_query:
            await update.callback_query.message.reply_text(BOT_NO_AUTORIZADO)
        return
    
    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    try:
        async with connection.cursor() as cursor:
            # Filtrar las inmersiones por el grupo activo (active_group)
            await cursor.execute("""
                SELECT inmersion_id, nombre, plazas 
                FROM inmersiones 
                WHERE active_group = %s
            """, (chat_id,))
            inmersiones = await cursor.fetchall()
        
        if not inmersiones:
            if update.message:
                message = await update.message.reply_text('No hay inmersiones disponibles para este grupo.', disable_notification=True)
            elif update.callback_query:
                message = await update.callback_query.message.reply_text('No hay inmersiones disponibles para este grupo.', disable_notification=True)
        else:
            # Variable para almacenar todo el mensaje
            texto_completo = ""

            for inmersion in inmersiones:
                inmersion_id, nombre, plazas = inmersion

                async with connection.cursor() as cursor:
                    # Obtener la lista de usuarios apuntados a la inmersión
                    await cursor.execute("""
                        SELECT username
                        FROM usuarios
                        WHERE inmersion_id = %s
                    """, (inmersion_id,))
                    usuarios = await cursor.fetchall()

                # Determinar el número de plazas restantes, considerando las 2 reservas
                plazas_disponibles = plazas - len(usuarios)
                plazas_disponibles_mostradas = max(plazas_disponibles, 0) - 2
                plazas_disponibles_mostradas = max(plazas_disponibles_mostradas, 0)

                # Crear el texto para esta inmersión
                texto = f'**{nombre}**\nPlazas restantes: {plazas_disponibles_mostradas}'

                if len(usuarios) > plazas:
                    texto += " (2 en reserva)\n"
                else:
                    texto += "\n"

                # Crear la lista de usuarios con marcadores de reserva si es necesario
                for i, (username,) in enumerate(usuarios):
                    if i == plazas - 2:
                        texto += f'- {username} (Reserva 1)\n'
                    elif i == plazas - 1:
                        texto += f'- {username} (Reserva 2)\n'
                    else:
                        texto += f'- {username}\n'

                # Agregar el texto al mensaje completo con un mayor espacio entre inmersiones
                texto_completo += texto + "\n---\n"

            # Añadir el mensaje informativo al final
            texto_completo += ("Para apuntarte, usa el comando /inmersiones, "
                               "para darte de baja, utiliza el comando /baja y "
                               "para informar de que necesitas equipo, puedes usar /alquilerequipo.")

            # Enviar todo el mensaje en un solo envío
            if private:
                message = await context.bot.send_message(chat_id=update.effective_user.id, text=texto_completo.strip(), parse_mode='Markdown', disable_notification=True)
            else:
                if update.message:
                    message = await update.message.reply_text(texto_completo.strip(), parse_mode='Markdown', disable_notification=True)
                elif update.callback_query:
                    message = await update.callback_query.message.reply_text(texto_completo.strip(), parse_mode='Markdown', disable_notification=True)

        # Anclar el mensaje si no es privado
        if not private and message:
            await context.bot.pin_chat_message(chat_id=chat_id, message_id=message.message_id, disable_notification=True)
        
    finally:
        connection.close()


# Comando /inmersiones
async def inmersiones(update: Update, context: ContextTypes.DEFAULT_TYPE, private=False):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO, disable_notification=True)
        return
    
    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Filtrar las inmersiones por el grupo activo (active_group)
        await cursor.execute("""
            SELECT i.inmersion_id, i.nombre, i.plazas, COUNT(u.user_id) AS inscritos
            FROM inmersiones i
            LEFT JOIN usuarios u ON i.inmersion_id = u.inmersion_id
            WHERE i.active_group = %s
            GROUP BY i.inmersion_id, i.nombre, i.plazas
        """, (chat_id,))
        inmersiones = await cursor.fetchall()
    
    if not inmersiones:
        await update.message.reply_text('No hay inmersiones disponibles para este grupo.', disable_notification=True)
    else:
        keyboard = []
        for inmersion in inmersiones:
            inmersion_id, nombre, plazas, inscritos = inmersion
            plazas_restantes = max(plazas - inscritos, 0)
            button_text = f"{nombre} - {plazas_restantes} plazas"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'apuntarse_{inmersion_id}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if private:
            await context.bot.send_message(chat_id=update.effective_user.id, text="Selecciona una inmersión:", reply_markup=reply_markup, disable_notification=True)
        else:
            await update.message.reply_text("Selecciona una inmersión:", reply_markup=reply_markup, disable_notification=True)
    
    connection.close()

# Manejador de la interacción con el botón "Apuntarse"
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    username = update.effective_user.first_name
    inmersion_id = query.data.split('_')[1]

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    try:
        async with connection.cursor() as cursor:
            # Obtener el nombre y las plazas disponibles de la inmersión
            await cursor.execute("SELECT nombre, plazas FROM inmersiones WHERE inmersion_id=%s", (inmersion_id,))
            inmersion = await cursor.fetchone()
            
            if inmersion is None:
                await query.edit_message_text(text='No se encontró ninguna inmersión con ese ID.')
                return

            nombre_inmersion, plazas_disponibles = inmersion

            # Verificar el número de usuarios ya registrados en la inmersión
            await cursor.execute("SELECT COUNT(*) FROM usuarios WHERE inmersion_id=%s", (inmersion_id,))
            usuarios_apuntados = await cursor.fetchone()

            # Calcular plazas disponibles considerando las 2 reservas
            plazas_restantes = max(plazas_disponibles - usuarios_apuntados[0] - 2, 0)

            if plazas_restantes <= 0:
                await query.edit_message_text(text=f'{username}, no hay plazas disponibles para la inmersión {nombre_inmersion}.')
                return

            # Verificar si el usuario ya está registrado en la inmersión
            await cursor.execute("SELECT COUNT(*) FROM usuarios WHERE inmersion_id=%s AND user_id=%s", (inmersion_id, user_id))
            (count,) = await cursor.fetchone()

            if count > 0:
                # Si el usuario ya está registrado, enviar un mensaje de aviso
                await query.edit_message_text(text=f'{username}, ya estás apuntado a la inmersión {nombre_inmersion}.')
            else:
                # Si el usuario no está registrado y hay plazas disponibles, insertar el nuevo registro
                await cursor.execute("INSERT INTO usuarios (inmersion_id, user_id, username) VALUES (%s, %s, %s)", (inmersion_id, user_id, username))
                await connection.commit()

                # Notificar al usuario en el chat
                await query.edit_message_text(text=f'{username}, te has apuntado a la inmersión {nombre_inmersion}.')
                try:
                    await context.bot.send_message(chat_id=user_id, text=f'Te has apuntado a la inmersión {nombre_inmersion}. Para darte de baja, usa el comando /baja {nombre_inmersion}.', disable_notification=True)
                except Forbidden:
                    # Si no puede enviar un mensaje privado, envía una respuesta en el grupo
                    await query.message.reply_text(f'{username}, te has apuntado a la inmersión {nombre_inmersion}. Para darte de baja, usa el comando /baja {nombre_inmersion} en este grupo.', disable_notification=True)
                # Llamando a /ver y anclando la nueva lista
                await ver(update, context)
    finally:
        connection.close()


# Comando /baja
async def baja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO)
        return

    user_id = update.effective_user.id

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Obtener las inmersiones a las que el usuario está apuntado y que pertenecen al grupo activo
        await cursor.execute("""
            SELECT i.inmersion_id, i.nombre
            FROM inmersiones i
            JOIN usuarios u ON i.inmersion_id = u.inmersion_id
            WHERE u.user_id = %s AND i.active_group = %s
        """, (user_id, chat_id))
        inmersiones = await cursor.fetchall()

    if not inmersiones:
        await update.message.reply_text("No estás apuntado a ninguna inmersión en este grupo.", disable_notification=True)
        connection.close()
        return

    # Crear botones para cada inmersión
    keyboard = [[InlineKeyboardButton(nombre, callback_data=f'baja_{inmersion_id}')] for inmersion_id, nombre in inmersiones]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Selecciona la inmersión de la que deseas darte de baja:", reply_markup=reply_markup, disable_notification=True)
    
    connection.close()

async def button_baja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data.split('_')
    inmersion_id = data[1]

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    try:
        async with connection.cursor() as cursor:
            # Obtener el nombre de la inmersión para confirmación
            await cursor.execute("SELECT nombre FROM inmersiones WHERE inmersion_id=%s", (inmersion_id,))
            inmersion = await cursor.fetchone()
            
            if inmersion is None:
                await query.edit_message_text(text="No se encontró ninguna inmersión con ese ID.")
                connection.close()
                return
            
            nombre_inmersion = inmersion[0]

            # Eliminar al usuario de la inmersión
            await cursor.execute("DELETE FROM usuarios WHERE inmersion_id=%s AND user_id=%s", (inmersion_id, user_id))
            await connection.commit()

        # Confirmar la baja al usuario
        await query.edit_message_text(text=f'Te has dado de baja de la inmersión {nombre_inmersion}.')
        # Llamando a /ver y anclando la nueva lista
        await ver(update, context)
    finally:
        connection.close()

# Comando /inmersiones_detalles (Solo Admin)
async def inmersiones_detalles(update: Update, context: ContextTypes.DEFAULT_TYPE, private=False):
    chat_id = update.effective_chat.id
    sender_user_id = update.effective_user.id  # ID del usuario que envía el comando

    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO, disable_notification=True)
        return
    
    if not await is_admin(sender_user_id, chat_id, context.bot):
        await update.message.reply_text(NO_ADMINISTRADOR, disable_notification=True)
        return
    
    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Filtrar las inmersiones por el grupo activo (active_group)
        await cursor.execute("""
            SELECT inmersion_id, nombre, plazas 
            FROM inmersiones 
            WHERE active_group = %s
        """, (chat_id,))
        inmersiones = await cursor.fetchall()
    
    if not inmersiones:
        await update.message.reply_text('No hay inmersiones disponibles para este grupo.', disable_notification=True)
        connection.close()
        return

    # Variable para almacenar todo el mensaje
    texto_completo = ""

    for inmersion in inmersiones:
        inmersion_id, nombre, plazas = inmersion

        async with connection.cursor() as cursor:
            # Obtener la lista de usuarios apuntados a la inmersión junto con sus observaciones
            await cursor.execute("""
                SELECT u.user_id, u.username, o.observacion
                FROM usuarios u
                LEFT JOIN observaciones o ON u.user_id = o.user_id AND o.inmersion_id = %s
                WHERE u.inmersion_id = %s
            """, (inmersion_id, inmersion_id))
            usuarios = await cursor.fetchall()

        # Construir el texto de la inmersión
        texto_completo += f'**{nombre}**\nPlazas restantes: {plazas - len(usuarios)}\n'
        for user_id, username, observacion in usuarios:
            texto_completo += f'- {username} (ID: {user_id}): {observacion if observacion else "Sin observaciones"}\n'
        
        texto_completo += "\n---\n"

    # Enviar el mensaje completo en modo silencioso
    if private:
        await context.bot.send_message(chat_id=update.effective_user.id, text=texto_completo.strip(), disable_notification=True)
    else:
        await update.message.reply_text(texto_completo.strip(), disable_notification=True)

    connection.close()

# Comando /crear_inmersion (Solo Admin)
async def crear_inmersion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    bot = context.bot

    # Verifica si update.message es None
    if update.message is None:
        await context.bot.send_message(chat_id=chat_id, text='Este comando solo se puede usar en un contexto de mensaje de texto.', disable_notification=True)
        return

    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO)
        return
    
    if not await is_admin(user_id, chat_id, bot):  # Await para la verificación de administrador
        await update.message.reply_text(NO_ADMINISTRADOR, disable_notification=True)
        return
    
    if len(context.args) < 2:  # Ahora se requieren solo dos argumentos: nombre y plazas
        await update.message.reply_text('Uso incorrecto. El uso correcto es: /crear_inmersion <Nombre del evento> <Plazas>', disable_notification=True)
        return
    
    nombre = ' '.join(context.args[:-1])  # Toma todos los argumentos menos el último como nombre
    plazas = context.args[-1]  # Toma el último argumento como plazas
    
    try:
        plazas = int(plazas)
    except ValueError:
        await update.message.reply_text('El número de plazas debe ser un número entero.', disable_notification=True)
        return
    
    # Verificar que el número de plazas no sea menor a 2
    if plazas < 2:
        await update.message.reply_text('No se puede crear una inmersión con menos de 2 plazas.', disable_notification=True)
        return
    
    # Obtener el timestamp actual
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Plazas de reserva
        plazas_con_reserva = plazas + 2
        # Insertar la inmersión con el campo active_group y el timestamp
        await cursor.execute("""
            INSERT INTO inmersiones (nombre, plazas, active_group, created_at) 
            VALUES (%s, %s, %s, %s)
        """, (nombre, plazas_con_reserva, chat_id, timestamp))
        await connection.commit()

        # Obtener el ID generado automáticamente
        await cursor.execute("SELECT LAST_INSERT_ID()")
        (evento_id,) = await cursor.fetchone()
    
    await update.message.reply_text(f'Inmersión creada: {nombre} (ID: {evento_id}, Plazas: {plazas}, Creada en: {timestamp}).', disable_notification=True)
    # Llamando a /ver y anclando la nueva lista
    await ver(update, context)
    connection.close()

# Comando /borrar_inmersion (Solo Admin)
async def borrar_inmersion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    bot = context.bot

    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO)
        return
    
    if not await is_admin(user_id, chat_id, bot):
        await update.message.reply_text(NO_ADMINISTRADOR, disable_notification=True)
        return    

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Filtrar las inmersiones por el grupo activo (active_group) y obtener el número de usuarios apuntados
        await cursor.execute("""
            SELECT i.inmersion_id, i.nombre, COUNT(u.user_id) as num_usuarios
            FROM inmersiones i
            LEFT JOIN usuarios u ON i.inmersion_id = u.inmersion_id
            WHERE i.active_group = %s
            GROUP BY i.inmersion_id, i.nombre
        """, (chat_id,))
        inmersiones = await cursor.fetchall()

    if not inmersiones:
        await update.message.reply_text("No hay inmersiones disponibles para borrar.", disable_notification=True)
        connection.close()
        return

    # Crear botones para cada inmersión con el número de usuarios apuntados
    keyboard = [
        [InlineKeyboardButton(f"{nombre} ({num_usuarios} usuarios)", callback_data=f'borrar_{inmersion_id}')]
        for inmersion_id, nombre, num_usuarios in inmersiones
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Selecciona una inmersión para borrarla:", reply_markup=reply_markup, disable_notification=True)
    
    connection.close()

async def button_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    inmersion_id = query.data.split('_')[1]

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    try:
        async with connection.cursor() as cursor:
            # Borrar la inmersión (las dependencias se manejarán por ON DELETE CASCADE en la base de datos)
            await cursor.execute("DELETE FROM inmersiones WHERE inmersion_id=%s", (inmersion_id,))
            await connection.commit()

        # Confirmar la eliminación al administrador
        await query.edit_message_text(text=f'La inmersión seleccionada ha sido borrada.')
        # Llamando a /ver y anclando la nueva lista
        await ver(update, context)
    finally:
        connection.close()

# Comando /observaciones (Solo Admin)
async def observaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bot = context.bot
    user_id = update.effective_user.id

    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO)
        return
    
    if not await is_admin(user_id, chat_id, bot):
        await update.message.reply_text(NO_ADMINISTRADOR, disable_notification=True)
        return

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Filtrar las inmersiones por el grupo activo (active_group)
        await cursor.execute("""
            SELECT inmersion_id, nombre 
            FROM inmersiones 
            WHERE active_group = %s
        """, (chat_id,))
        inmersiones = await cursor.fetchall()

    if not inmersiones:
        await update.message.reply_text("No hay inmersiones disponibles.", disable_notification=True)
        connection.close()
        return

    # Crear botones para cada inmersión
    keyboard = [[InlineKeyboardButton(nombre, callback_data=f'select_inmersion_{inmersion_id}')] for inmersion_id, nombre in inmersiones]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Selecciona una inmersión para ver los usuarios apuntados:", reply_markup=reply_markup, disable_notification=True)
    
    connection.close()

async def select_inmersion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    inmersion_id = query.data.split('_')[2]
    context.user_data['selected_inmersion'] = inmersion_id

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Obtener usuarios apuntados a la inmersión seleccionada
        await cursor.execute("SELECT user_id, username FROM usuarios WHERE inmersion_id=%s", (inmersion_id,))
        usuarios = await cursor.fetchall()

    if not usuarios:
        await query.edit_message_text("No hay usuarios apuntados a esta inmersión.")
        connection.close()
        return

    # Crear botones para cada usuario
    keyboard = [[InlineKeyboardButton(username, callback_data=f'select_user_{user_id}')] for user_id, username in usuarios]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Selecciona un usuario para agregar o modificar la observación:", reply_markup=reply_markup)
    
    connection.close()

async def select_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.data.split('_')[2]
    context.user_data['selected_user'] = user_id

    await query.edit_message_text(f"Escribe la observación para el usuario seleccionado:")

    return 'WAITING_FOR_OBSERVATION'

async def handle_observation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    observacion = update.message.text
    inmersion_id = context.user_data['selected_inmersion']
    user_id = context.user_data['selected_user']

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    try:
        async with connection.cursor() as cursor:
            # Comprobar si ya existe una observación para este user_id y evento_id
            await cursor.execute("SELECT COUNT(*) FROM observaciones WHERE inmersion_id=%s AND user_id=%s", 
                                 (inmersion_id, user_id))
            (count,) = await cursor.fetchone()

            if count > 0:
                # Si ya existe, actualizar la observación existente
                await cursor.execute("UPDATE observaciones SET observacion=%s WHERE inmersion_id=%s AND user_id=%s", 
                                     (observacion, inmersion_id, user_id))
                await update.message.reply_text(f'Observación actualizada para el usuario en la inmersión seleccionada.', disable_notification=True)
            else:
                # Si no existe, insertar una nueva observación
                await cursor.execute("INSERT INTO observaciones (inmersion_id, user_id, observacion) VALUES (%s, %s, %s)", 
                                     (inmersion_id, user_id, observacion))
                await update.message.reply_text(f'Observación añadida para el usuario en la inmersión seleccionada.', disable_notification=True)
            
            await connection.commit()
    finally:
        connection.close()

# Comando /eliminar_usuario (Solo Admin)
async def eliminar_buceador(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sender_user_id = update.effective_user.id  # ID del usuario que envía el comando
    bot = context.bot

    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO)
        return
    
    if not await is_admin(sender_user_id, chat_id, bot):
        await update.message.reply_text(NO_ADMINISTRADOR, disable_notification=True)
        return
    
    if len(context.args) != 2:
        await update.message.reply_text('Uso incorrecto. El uso correcto es: /eliminar_buceador <ID del evento> <ID del usuario>', disable_notification=True)
        return
    
    evento_id = context.args[0]
    user_id = context.args[1]
    
    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Verificar si la inmersión pertenece al grupo activo
        await cursor.execute("SELECT 1 FROM inmersiones WHERE inmersion_id=%s AND active_group=%s", (evento_id, chat_id))
        valid_inmersion = await cursor.fetchone()

        if not valid_inmersion:
            await update.message.reply_text('No tienes autorización para eliminar usuarios de esta inmersión.', disable_notification=True)
            connection.close()
            return

        # Proceder a eliminar el usuario de la inmersión
        await cursor.execute("DELETE FROM observaciones WHERE inmersion_id=%s AND user_id=%s", (evento_id, user_id))
        await cursor.execute("DELETE FROM usuarios WHERE inmersion_id=%s AND user_id=%s", (evento_id, user_id))
        await connection.commit()
    
    await update.message.reply_text(f'Usuario {user_id} eliminado de la inmersión {evento_id}.', disable_notification=True)
    connection.close()

# Comando /purgar_datos (Solo Admin)
async def purgar_datos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sender_user_id = update.effective_user.id
    bot = context.bot

    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO)
        return
    
    if not await is_admin(sender_user_id, chat_id, bot):
        await update.message.reply_text(NO_ADMINISTRADOR, disable_notification=True)
        return

    # Crear un botón de confirmación con un icono de radioactivo
    keyboard = [
        [InlineKeyboardButton("☢️ Sí, estoy seguro", callback_data='confirmar_purgar')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("⚠️ ¿Estás seguro de que deseas purgar todos los datos del sistema?", reply_markup=reply_markup, disable_notification=True)

# Paso 2: Ejecutar la purga de datos si se confirma
async def confirmar_purgar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id  # Obtener el chat_id del grupo o chat activo

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    try:
        async with connection.cursor() as cursor:
            # Eliminar observaciones, usuarios e inmersiones que pertenezcan al grupo activo
            await cursor.execute("""
                DELETE o 
                FROM observaciones o
                JOIN inmersiones i ON o.inmersion_id = i.inmersion_id
                WHERE i.active_group = %s
            """, (chat_id,))

            await cursor.execute("""
                DELETE u 
                FROM usuarios u
                JOIN inmersiones i ON u.inmersion_id = i.inmersion_id
                WHERE i.active_group = %s
            """, (chat_id,))

            await cursor.execute("""
                DELETE FROM inmersiones 
                WHERE active_group = %s
            """, (chat_id,))

            await connection.commit()

        # Confirmar la eliminación al administrador
        await query.edit_message_text(text='☢️ Todos los datos del grupo han sido purgados del sistema.')
    finally:
        connection.close()


# El usuario podrá marcar la inmersión en la que necesita equipo.
async def alquilerequipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not authorized(chat_id):
        await update.message.reply_text(BOT_NO_AUTORIZADO)
        return
    
    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    async with connection.cursor() as cursor:
        # Obtener las inmersiones a las que el usuario está apuntado y que pertenecen al grupo activo
        await cursor.execute("""
            SELECT i.inmersion_id, i.nombre
            FROM inmersiones i
            JOIN usuarios u ON i.inmersion_id = u.inmersion_id
            WHERE u.user_id = %s AND i.active_group = %s
        """, (user_id, chat_id))
        inmersiones = await cursor.fetchall()

    if not inmersiones:
        await update.message.reply_text("No estás apuntado a ninguna inmersión en este grupo.", disable_notification=True)
        connection.close()
        return

    # Crear botones para cada inmersión del grupo activo
    keyboard = [[InlineKeyboardButton(nombre, callback_data=f'equipo_{inmersion_id}')] for inmersion_id, nombre in inmersiones]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("¿En qué inmersión necesitas equipo?", reply_markup=reply_markup, disable_notification=True)
    
    connection.close()

async def button_equipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data.split('_')
    inmersion_id = data[1]

    connection = await aiomysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

    try:
        async with connection.cursor() as cursor:
            # Comprobar si ya existe un registro en observaciones
            await cursor.execute("SELECT COUNT(*) FROM observaciones WHERE inmersion_id=%s AND user_id=%s", 
                                 (inmersion_id, user_id))
            (count,) = await cursor.fetchone()

            if count > 0:
                # Si ya existe un registro, informar al usuario
                await query.edit_message_text(text="Ya habías informado que necesitas equipo para esta inmersión.")
            else:
                # Insertar en la tabla observaciones
                await cursor.execute("INSERT INTO observaciones (inmersion_id, user_id, observacion) VALUES (%s, %s, %s)", 
                                     (inmersion_id, user_id, "Necesita equipo"))
                await connection.commit()

                # Confirmar la acción al usuario
                await query.edit_message_text(text="Se ha registrado que necesitas equipo en la inmersión seleccionada.")
    finally:
        connection.close()

# Ejecutar el bot
def main():
    # Crear la aplicación usando el nuevo enfoque asíncrono
    application = Application.builder().token(TOKEN).build()
    
    # Registrar los manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ver", ver))
    application.add_handler(CommandHandler("inmersiones", inmersiones))
    application.add_handler(CommandHandler("baja", baja))
    application.add_handler(CallbackQueryHandler(button_baja, pattern="^baja_"))
    application.add_handler(CommandHandler("inmersiones_detalles", inmersiones_detalles))
    application.add_handler(CommandHandler("crear_inmersion", crear_inmersion))
    application.add_handler(CommandHandler("borrar_inmersion", borrar_inmersion))
    application.add_handler(CallbackQueryHandler(button_borrar, pattern="^borrar_"))
    application.add_handler(CommandHandler("observaciones", observaciones))
    application.add_handler(CallbackQueryHandler(select_inmersion, pattern="^select_inmersion_"))
    application.add_handler(CallbackQueryHandler(select_user, pattern="^select_user_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_observation))
    application.add_handler(CommandHandler("eliminar_buceador", eliminar_buceador))
    application.add_handler(CommandHandler("purgar_datos", purgar_datos))
    application.add_handler(CallbackQueryHandler(confirmar_purgar, pattern='^confirmar_purgar$'))
    application.add_handler(CommandHandler("alquilerequipo", alquilerequipo))
    application.add_handler(CallbackQueryHandler(button_equipo, pattern="^equipo_"))
    application.add_handler(CallbackQueryHandler(button, pattern='^apuntarse_'))

    # Ejecutar el bot en modo polling
    application.run_polling()

if __name__ == '__main__':
    main()