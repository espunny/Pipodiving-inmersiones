from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import os

TOKEN = os.getenv('TOKEN') # TOKEN DE TELEGRAM
AUTHORIZED_GROUP_ID = int(os.getenv('AUTHORIZED_GROUP_ID'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # URL del webhook

# Estado global de eventos
EVENTS = {}
ADMIN_IDS = {int(admin_id) for admin_id in os.getenv('ADMIN_IDS', '').split(',')} # Id de los administradores

#Para obtener el ID del grupo
async def get_chat_id(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"El chat_id de este grupo es: {chat_id}")

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_GROUP_ID:
        await update.message.reply_text("Este bot solo está autorizado para funcionar en un grupo específico.")
        #return
    await update.message.reply_text("¡Hola! Usa /inmersiones para ver los detalles de los eventos.")
    await update.message.reply_text('¡Hola! Usa /inmersiones para ver los detalles de los eventos.')


async def inmersiones(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_GROUP_ID:
        await update.message.reply_text("Este bot solo está autorizado para funcionar en un grupo específico.")
        return
    user_id = update.effective_user.id

    if not EVENTS:
        await update.message.reply_text('No hay eventos disponibles.')
        return

    for event_id, event in EVENTS.items():
        text = (f"Evento ID: {event_id}\n"
                f"Nombre: {event['name']}\n"
                f"Plazas restantes: {event['spots_left']}\n"
                f"Usuarios apuntados: {len(event['registered_users'])}")

        # Obtener información de los usuarios apuntados
        user_names = []
        for uid in event['registered_users']:
            user = await context.bot.get_chat_member(update.effective_chat.id, uid)
            if user:
                user_names.append(f"- {user.user.full_name} (ID: {uid})")

        if user_names:
            user_names_list = '\n'.join(user_names)
            text += f"\nUsuarios apuntados:\n{user_names_list}"

        buttons = []
        if user_id in event['registered_users']:
            buttons.append(InlineKeyboardButton("Desapuntarme", callback_data=f'unregister_{event_id}'))
        else:
            if event['spots_left'] > 0:
                buttons.append(InlineKeyboardButton("Apuntarme", callback_data=f'register_{event_id}'))

        if buttons:
            reply_markup = InlineKeyboardMarkup([buttons])
            await update.message.reply_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text)
    user_id = update.effective_user.id

    if not EVENTS:
        await update.message.reply_text('No hay eventos disponibles.')
        return

    for event_id, event in EVENTS.items():
        text = (f"Evento ID: {event_id}\n"
                f"Nombre: {event['name']}\n"
                f"Plazas restantes: {event['spots_left']}\n"
                f"Usuarios apuntados: {len(event['registered_users'])}")

        # Obtener información de los usuarios apuntados
        user_names = []
        for uid in event['registered_users']:
            user = await context.bot.get_chat_member(update.effective_chat.id, uid)
            if user:
                user_names.append(f"- {user.user.full_name} (ID: {uid})")

        if user_names:
            user_names_list = '\n'.join(user_names)
            text += f"\nUsuarios apuntados:\n{user_names_list}"

        buttons = []
        if user_id in event['registered_users']:
            buttons.append(InlineKeyboardButton("Desapuntarme", callback_data=f'unregister_{event_id}'))
        else:
            if event['spots_left'] > 0:
                buttons.append(InlineKeyboardButton("Apuntarme", callback_data=f'register_{event_id}'))

        if buttons:
            reply_markup = InlineKeyboardMarkup([buttons])
            await update.message.reply_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text)

async def crear_inmersion(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("No tienes permiso para crear inmersiones.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /crear_inmersion <nombre> <plazas>")
        return

    event_name = context.args[0]
    try:
        max_spots = int(context.args[1])
        if max_spots <= 0 or max_spots > 10:
            await update.message.reply_text("El número de plazas debe ser entre 1 y 10.")
            return
    except ValueError:
        await update.message.reply_text("Por favor, introduce un número válido de plazas.")
        return

    event_id = len(EVENTS) + 1
    EVENTS[event_id] = {
        'name': event_name,
        'spots_left': max_spots,
        'registered_users': set(),
        'blacklisted_users': set()
    }

    await update.message.reply_text(f"Nuevo evento creado:\nNombre: {event_name}\nPlazas restantes: {max_spots}")

async def borrar_inmersion(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("No tienes permiso para borrar inmersiones.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /borrar_inmersion <ID>")
        return

    try:
        event_id = int(context.args[0])
        if event_id in EVENTS:
            del EVENTS[event_id]
            await update.message.reply_text(f"Inmersión con ID {event_id} ha sido borrada.")
        else:
            await update.message.reply_text("Inmersión no encontrada.")
    except ValueError:
        await update.message.reply_text("Por favor, introduce un número válido de ID.")

async def eliminar_usuario(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("No tienes permiso para eliminar usuarios.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Uso: /eliminar_usuario <evento_id> <user_id>")
        return

    try:
        event_id = int(context.args[0])
        target_user_id = int(context.args[1])
        
        if event_id in EVENTS:
            event = EVENTS[event_id]
            if target_user_id in event['registered_users']:
                event['registered_users'].remove(target_user_id)
                event['spots_left'] += 1
                event['blacklisted_users'].add(target_user_id)  # Añadir al blacklist
                await update.message.reply_text(f"Usuario con ID {target_user_id} ha sido eliminado del evento {event_id}.")
                # Notificar al usuario eliminado
                try:
                    await context.bot.send_message(target_user_id, f"Has sido eliminado del evento ID {event_id}.")
                except Exception as e:
                    print(f"No se pudo enviar el mensaje al usuario: {e}")
            else:
                await update.message.reply_text("Usuario no está apuntado en este evento.")
        else:
            await update.message.reply_text("Evento no encontrado.")
    except ValueError:
        await update.message.reply_text("Por favor, introduce números válidos para ID de evento y usuario.")

async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    event_id = int(query.data.split('_')[1])

    if event_id not in EVENTS:
        await query.answer("Evento no encontrado.")
        return

    event = EVENTS[event_id]

    if user_id in event['blacklisted_users']:
        await query.answer("No puedes apuntarte a este evento.")
        return

    if query.data.startswith('register'):
        if user_id in event['registered_users']:
            await query.answer("¡Ya estás apuntado!")
        elif event['spots_left'] > 0:
            event['registered_users'].add(user_id)
            event['spots_left'] -= 1
            await query.answer("¡Te has apuntado con éxito!")
            # Enviar mensaje privado de confirmación
            try:
                await context.bot.send_message(user_id, f"Te has apuntado con éxito al evento ID {event_id}.")
            except Exception as e:
                print(f"No se pudo enviar el mensaje al usuario: {e}")
        else:
            await query.answer("Lo siento, no hay más plazas disponibles.")
    elif query.data.startswith('unregister'):
        if user_id not in event['registered_users']:
            await query.answer("No estás apuntado en este evento.")
        else:
            event['registered_users'].remove(user_id)
            event['spots_left'] += 1
            await query.answer("¡Te has desapuntado con éxito!")
            # Enviar mensaje privado de confirmación
            try:
                await context.bot.send_message(user_id, f"Te has desapuntado del evento ID {event_id}.")
            except Exception as e:
                print(f"No se pudo enviar el mensaje al usuario: {e}")

    # Actualizar el mensaje con la información del evento
    text = (f"Evento ID: {event_id}\n"
            f"Nombre: {event['name']}\n"
            f"Plazas restantes: {event['spots_left']}\n"
            f"Usuarios apuntados: {len(event['registered_users'])}")

    # Obtener información de los usuarios apuntados
    user_names = []
    for uid in event['registered_users']:
        user = await context.bot.get_chat_member(update.effective_chat.id, uid)
        if user:
            user_names.append(f"- {user.user.full_name}")

    if user_names:
        user_names_list = '\n'.join(user_names)
        text += f"\nUsuarios apuntados:\n{user_names_list}"

    buttons = []
    if user_id in event['registered_users']:
        buttons.append(InlineKeyboardButton("Desapuntarme", callback_data=f'unregister_{event_id}'))
    else:
        if event['spots_left'] > 0:
            buttons.append(InlineKeyboardButton("Apuntarme", callback_data=f'register_{event_id}'))

    reply_markup = InlineKeyboardMarkup([buttons])
    await query.edit_message_text(text, reply_markup=reply_markup)

async def agregar_admin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        if len(context.args) != 1:
            await update.message.reply_text("Uso: /agregar_admin <ID>")
            return

        try:
            new_admin_id = int(context.args[0])
            ADMIN_IDS.add(new_admin_id)
            await update.message.reply_text(f"Administrador con ID {new_admin_id} añadido.")
        except ValueError:
            await update.message.reply_text("Por favor, introduce un número válido de ID.")
    else:
        await update.message.reply_text("No tienes permiso para usar este comando.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('inmersiones', inmersiones))
    application.add_handler(CommandHandler('crear_inmersion', crear_inmersion))
    application.add_handler(CommandHandler('borrar_inmersion', borrar_inmersion))
    application.add_handler(CommandHandler('eliminar_usuario', eliminar_usuario))
    application.add_handler(CommandHandler('agregar_admin', agregar_admin))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(CommandHandler('getchatid', get_chat_id))

    # Configurar el webhook en lugar de run_polling
    application.run_webhook(
        listen="0.0.0.0",  # Escuchar en todas las interfaces
        port=int(os.getenv('PORT', '8443')),  # Usar el puerto 8443 por defecto
        url_path=TOKEN,  # Usar el token como parte de la URL del webhook
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"  # La URL completa para el webhook
    )

if __name__ == '__main__':
    main()
