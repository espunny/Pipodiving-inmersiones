
import os
import pymysql
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Filters, MessageHandler, Updater

# Variables del sistema
TOKEN = os.getenv('TOKEN')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
AUTHORIZED_GROUP_ID = os.getenv('AUTHORIZED_GROUP_ID')
AUTHORIZED_CHAT_ID = os.getenv('AUTHORIZED_CHAT_ID')

# Saber si un usuario es administrador
def is_admin(user_id, chat_id, bot):
    chat_administrators = bot.get_chat_administrators(chat_id)
    for admin in chat_administrators:
        if admin.user.id == user_id:
            return True
    return False

# Conectar a la base de datos
def connect_db():
    return pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DATABASE)

# Verificación de autorización
def authorized(chat_id):
    return str(chat_id) == AUTHORIZED_GROUP_ID or str(chat_id) in AUTHORIZED_CHAT_ID.split(',')

# Función de inicio
def start(update: Update, context):
    chat_id = update.effective_chat.id
    update.message.reply_text(f'Bienvenido! Tu chat_id es {chat_id}.')

# Comando /ver
def ver(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return

    user_id = update.effective_user.id
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM inmersiones")
        inmersiones = cursor.fetchall()
    
    if not inmersiones:
        context.bot.send_message(chat_id=user_id, text='No hay inmersiones disponibles.')
    else:
        for inmersion in inmersiones:
            inmersion_id, nombre, plazas = inmersion
            cursor.execute("SELECT user_id, username, observacion FROM usuarios LEFT JOIN observaciones ON usuarios.user_id = observaciones.user_id WHERE inmersion_id=%s", (inmersion_id,))
            usuarios = cursor.fetchall()
            
            texto = f'Inmersión: {nombre}\\nPlazas restantes: {plazas - len(usuarios)}'
            for usuario in usuarios:
                user_id, username, observacion = usuario
                texto += f'\\n- {username} (User ID: {user_id}): {observacion}'
            
            keyboard = [[InlineKeyboardButton("🤿 Apuntarse", callback_data=f'apuntarse_{inmersion_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=user_id, text=texto, reply_markup=reply_markup)
    
    connection.close()


# Comando /inmersiones
def inmersiones(update: Update, context, private=False):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM inmersiones")
        inmersiones = cursor.fetchall()
    
    if not inmersiones:
        update.message.reply_text('No hay inmersiones disponibles.')
    else:
        for inmersion in inmersiones:
            inmersion_id, nombre, plazas = inmersion
            cursor.execute("SELECT * FROM usuarios WHERE inmersion_id=%s", (inmersion_id,))
            usuarios = cursor.fetchall()
            
            texto = f'Inmersión: {nombre}\nPlazas restantes: {plazas - len(usuarios)}'
            for usuario in usuarios:
                user_id, inmersion_id, observacion = usuario
                texto += f'\n- Usuario ID {user_id}: {observacion}'
            
            keyboard = [[InlineKeyboardButton("🤿 Apuntarse", callback_data=f'apuntarse_{inmersion_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if private:
                context.bot.send_message(chat_id=update.effective_user.id, text=texto, reply_markup=reply_markup)
            else:
                update.message.reply_text(texto, reply_markup=reply_markup)
    
    connection.close()

# Comando /baja
def baja(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    if len(context.args) != 1:
        update.message.reply_text('Uso incorrecto. El uso correcto es: /baja <ID del evento>')
        return
    
    evento_id = context.args[0]
    user_id = update.effective_user.id
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM usuarios WHERE inmersion_id=%s AND user_id=%s", (evento_id, user_id))
        connection.commit()
    
    update.message.reply_text(f'Te has dado de baja de la inmersión con ID {evento_id}.')
    connection.close()

# Comando /inmersiones_detalles (Solo Admin)
def inmersiones_detalles(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM inmersiones")
        inmersiones = cursor.fetchall()
    
    if not inmersiones:
        update.message.reply_text('No hay inmersiones disponibles.')
    else:
        for inmersion in inmersiones:
            inmersion_id, nombre, plazas = inmersion
            cursor.execute("SELECT user_id, username, observacion FROM usuarios LEFT JOIN observaciones ON usuarios.user_id = observaciones.user_id WHERE inmersion_id=%s", (inmersion_id,))
            usuarios = cursor.fetchall()
            
            texto = f'Inmersión: {nombre}\\nPlazas restantes: {plazas - len(usuarios)}'
            for usuario in usuarios:
                user_id, username, observacion = usuario
                texto += f'\\n- {username} (User ID: {user_id}): {observacion}'
            
            update.message.reply_text(texto)
    
    connection.close()

# Comando /crear_inmersion (Solo Admin)
def crear_inmersion(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    if not is_admin(user_id, chat_id, bot):
        update.message.reply_text('No tienes autorización para usar este comando.')
        return
    
    if len(context.args) < 3:
        update.message.reply_text('Uso incorrecto. El uso correcto es: /crear_inmersion <ID del evento> <Nombre del evento> <Plazas>')
        return
    
    evento_id = context.args[0]
    nombre = ' '.join(context.args[1:-1])
    plazas = context.args[-1]
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO inmersiones (inmersion_id, nombre, plazas) VALUES (%s, %s, %s)", (evento_id, nombre, plazas))
        connection.commit()
    
    update.message.reply_text(f'Inmersión creada: {nombre} (ID: {evento_id}, Plazas: {plazas}).')
    connection.close()

# Comando /borrar_inmersion (Solo Admin)
def borrar_inmersion(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    if not is_admin(user_id, chat_id, bot):
        update.message.reply_text('No tienes autorización para usar este comando.')
        return    

    if len(context.args) != 1:
        update.message.reply_text('Uso incorrecto. El uso correcto es: /borrar_inmersion <ID del evento>')
        return
    
    evento_id = context.args[0]
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM observaciones WHERE inmersion_id=%s", (evento_id,))
        cursor.execute("DELETE FROM usuarios WHERE inmersion_id=%s", (evento_id,))
        cursor.execute("DELETE FROM inmersiones WHERE inmersion_id=%s", (evento_id,))
        connection.commit()
    
    update.message.reply_text(f'Inmersión con ID {evento_id} ha sido borrada.')
    connection.close()

# Comando /observaciones (Solo Admin)
def observaciones(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    if not is_admin(user_id, chat_id, bot):
        update.message.reply_text('No tienes autorización para usar este comando.')
        return

    if len(context.args) < 3:
        update.message.reply_text('Uso incorrecto. El uso correcto es: /observaciones <ID del evento> <ID del usuario> <Observaciones>')
        return
    
    evento_id = context.args[0]
    user_id = context.args[1]
    observacion = ' '.join(context.args[2:])
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO observaciones (inmersion_id, user_id, observacion) VALUES (%s, %s, %s)", (evento_id, user_id, observacion))
        connection.commit()
    
    update.message.reply_text(f'Observación añadida para el usuario {user_id} en la inmersión {evento_id}.')
    connection.close()

# Comando /eliminar_usuario (Solo Admin)
def eliminar_usuario(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    if not is_admin(user_id, chat_id, bot):
        update.message.reply_text('No tienes autorización para usar este comando.')
        return
    
    if len(context.args) != 2:
        update.message.reply_text('Uso incorrecto. El uso correcto es: /eliminar_usuario <ID del evento> <ID del usuario>')
        return
    
    evento_id = context.args[0]
    user_id = context.args[1]
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM observaciones WHERE inmersion_id=%s AND user_id=%s", (evento_id, user_id))
        cursor.execute("DELETE FROM usuarios WHERE inmersion_id=%s AND user_id=%s", (evento_id, user_id))
        connection.commit()
    
    update.message.reply_text(f'Usuario {user_id} eliminado de la inmersión {evento_id}.')
    connection.close()

# Comando /purgar_datos (Solo Admin)
def purgar_datos(update: Update, context):
    chat_id = update.effective_chat.id
    if not authorized(chat_id):
        update.message.reply_text('No tienes autorización para usar este bot.')
        return
    
    if not is_admin(user_id, chat_id, bot):
        update.message.reply_text('No tienes autorización para usar este comando.')
        return
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM observaciones")
        cursor.execute("DELETE FROM usuarios")
        cursor.execute("DELETE FROM inmersiones")
        connection.commit()
    
    update.message.reply_text('Todos los datos han sido purgados del sistema.')
    connection.close()

# Manejar la respuesta del botón "Apuntarse"
def button(update: Update, context):
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    username = query.from_user.username  # Obtener el nombre de usuario
    inmersion_id = query.data.split('_')[1]
    
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO usuarios (inmersion_id, user_id, username) VALUES (%s, %s, %s)", (inmersion_id, user_id, username))
        connection.commit()
    
    query.edit_message_text(text=f'Te has apuntado a la inmersión {inmersion_id}.')
    context.bot.send_message(chat_id=user_id, text=f'Te has apuntado a la inmersión {inmersion_id}. Para darte de baja, usa el comando /baja {inmersion_id}.')
    
    connection.close()

# Ejecutar el bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ver", ver))
    dp.add_handler(CommandHandler("inmersiones", inmersiones))
    dp.add_handler(CommandHandler("baja", baja))
    dp.add_handler(CommandHandler("inmersiones_detalles", inmersiones_detalles))
    dp.add_handler(CommandHandler("crear_inmersion", crear_inmersion))
    dp.add_handler(CommandHandler("borrar_inmersion", borrar_inmersion))
    dp.add_handler(CommandHandler("observaciones", observaciones))
    dp.add_handler(CommandHandler("eliminar_usuario", eliminar_usuario))
    dp.add_handler(CommandHandler("purgar_datos", purgar_datos))
    dp.add_handler(CallbackQueryHandler(button, pattern='^apuntarse_'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
