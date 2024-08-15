# Pipodiving-inmersiones Alpha V1
Support on Telegram @t850model102

Bot de Telegram para gestionar inmersiones de un club de buceo.
Esta es una versión preliminar que aún no tiene persistencia.

Se agradece cualquier idea o aportación.
Se puede probar el funcionamiento en el siguiente grupo privado (Se requiere verificación).
https://t.me/+-1Yp622bPi5iMDc0

--------
Telegram bot to manage dives of a diving club.
This is a preliminary version that does not yet have persistence. 

Contributions are welcome.
You can test the operation in the following private group (Verification required).
https://t.me/+-1Yp622bPi5iMDc0
--------

COMANDOS:
1.	/start
	•	Descripción: Envía un mensaje de bienvenida y una breve explicación sobre el uso del bot.
	•	Ejemplo de uso: /start
	•	Respuesta esperada: “¡Hola! Usa /inmersiones para ver los detalles de los eventos.”
 
2.	/inmersiones
	•	Descripción: Muestra una lista de eventos disponibles, incluyendo los detalles y la opción de apuntarse o desapuntarse.
	•	Ejemplo de uso: /inmersiones

3.	/crear_inmersion  
	•	Descripción: Crea un nuevo evento con un nombre y un número específico de plazas.
	•	Ejemplo de uso: /crear_inmersion Taller de JavaScript 5
	•	Respuesta esperada: “Nuevo evento creado:\nNombre: Taller de JavaScript\nPlazas restantes: 5”

4.	/borrar_inmersion 
	•	Descripción: Borra un evento existente especificado por su ID.
	•	Ejemplo de uso: /borrar_inmersion 1
	•	Respuesta esperada: “Inmersión con ID 1 ha sido borrada.”

5.	/eliminar_usuario <evento_id> <user_id>
	•	Descripción: Elimina un usuario de un evento especificado por el ID del evento y el ID del usuario. Además, el usuario es añadido a una lista negra.
	•	Ejemplo de uso: /eliminar_usuario 1 123456789
	•	Respuesta esperada: “Usuario con ID 123456789 ha sido eliminado del evento 1.”

6.	/agregar_admin 
	•	Descripción: Añade un nuevo administrador al bot. Solo disponible para los administradores existentes.
	•	Ejemplo de uso: /agregar_admin 987654321
	•	Respuesta esperada: “Administrador con ID 987654321 añadido.”

LIMITACIONES: ¡Atención, este bot está en versión alpha y aún no tiene persistencia! por lo que cuando se reinicie, se perderán todos los datos de las inmersiones.
