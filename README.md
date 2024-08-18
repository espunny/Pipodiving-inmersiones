Maria DB version. Beta2
Support on Telegram @t850model102

Bot de Telegram para gestionar inmersiones de un club de buceo.
Esta es una versión preliminar.

Se agradece cualquier idea o aportación.
Se puede probar el funcionamiento en el siguiente grupo privado. Solamente hay que poner el símbolo "/" o pinchar en el icono de comandos y se mostrarán los comandos disponibles.
[https://t.me/+pAmFphtBgNo5MDU8](https://t.me/+pAmFphtBgNo5MDU8)

En esta versión los administradores del grupo, son los administradores del bot.

Si intentas añadir el bot a tu grupo, no funcionará. Tendrás que crear tu propio bot con el código fuente de esta página y asignar el ID de tu Grupo en las variables de tu SO.
Si necesitas ayuda profesional para implantarlo en tu grupo de telegram, puedes contactar conmigo en privado por Telegram: @t850model102

--------
Telegram bot to manage dives of a diving club.
This is a preliminary version.

Contributions are welcome.
You can test the operation in the following private group.
[https://t.me/+pAmFphtBgNo5MDU8](https://t.me/+pAmFphtBgNo5MDU8)

Bot de Gestión de Inmersiones

Este bot de Telegram está diseñado para gestionar inmersiones y usuarios registrados en ellas. Permite a los usuarios ver las inmersiones disponibles, registrarse en ellas, añadir observaciones, y más. Algunas funciones son exclusivas para administradores.

Requisitos

Asegúrate de tener instalado Python 3.8 o superior. Las dependencias del proyecto se manejan a través de pip y están listadas en requirements.txt.

Instalación

	1.	Clona este repositorio:
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
	2.	Crea un entorno virtual:
python3 -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
	3.	Instala las dependencias:
pip install -r requirements.txt
	4.	Configura las variables de entorno:
Crea un archivo .env en la raíz del proyecto y define las siguientes variables:
TOKEN=your_telegram_bot_token
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_mysql_database_name
AUTHORIZED_GROUP_ID=your_authorized_group_id
AUTHORIZED_CHAT_ID=your_authorized_chat_id

Ejecución del Bot

Para ejecutar el bot, asegúrate de que tu entorno virtual esté activado y ejecuta:

python bot.py

Comandos Disponibles

Comandos Generales

/start: Inicia el bot y muestra un mensaje de bienvenida. Muestra el chat_id del grupo autorizado.

/inmersiones: Muestra una lista de todas las inmersiones disponibles, incluyendo los usuarios registrados y el número de plazas restantes. Se muestra un botón con el icono de un buceador para apuntarse a la inmersión.

/ver: Muestra la misma información que /inmersiones, pero en un chat privado.

/baja: Permite a un usuario darse de baja de una inmersión. El bot muestra botones con las inmersiones en las que el usuario está inscrito, permitiendo elegir de cuál darse de baja.

/alquilerequipo: Permite a los usuarios informar que necesitan equipo para una inmersión específica. El usuario verá botones con las inmersiones en las que está inscrito y puede seleccionar la inmersión para registrar la observación “Necesita equipo”.

Comandos Exclusivos para Administradores

Estos comandos solo pueden ser ejecutados por administradores:

/inmersiones_detalles: Similar al comando /inmersiones, pero además de la información básica, muestra los user_id de los buceadores inscritos.

/crear_inmersion  : Crea una nueva inmersión con el nombre especificado y con un número determinado de plazas.

/borrar_inmersion: Muestra una lista de inmersiones con el número de usuarios inscritos. Al seleccionar una inmersión, esta se borra del sistema.

/observaciones: Muestra una lista de inmersiones. Al seleccionar una inmersión, se muestra una lista de usuarios inscritos. Al seleccionar un usuario, se le pedirá al administrador que escriba una observación, la cual se guardará en la base de datos.

/eliminar_buceador  : Elimina a un usuario específico de una inmersión. Si tiene observaciones, se eliminan también.

/purgar_datos: Purga todos los datos de inmersiones, usuarios y observaciones del sistema. Antes de purgar, el bot solicita confirmación mediante un botón con un icono de radioactivo.

Ejemplo de Uso

	1.	Crear una inmersión (solo para administradores):
/crear_inmersion “Buceo en arrecife” 10
	2.	Ver inmersiones disponibles:
/inmersiones
	3.	Apuntarse a una inmersión:
Simplemente pulsa el botón “🤿 Apuntarse” junto a la inmersión en la que deseas inscribirte.
	4.	Darse de baja de una inmersión:
/baja
Selecciona la inmersión de la que deseas darte de baja.
	5.	Informar que necesitas equipo:
/alquilerequipo
Selecciona la inmersión para la que necesitas equipo.
	6.	Purgar datos del sistema (solo para administradores):
/purgar_datos
Confirma la acción para eliminar todos los datos.

Consideraciones

Asegúrate de que el bot solo se utilice en los grupos autorizados, definidos en las variables de entorno.
Solo los administradores pueden ejecutar comandos críticos como la creación, eliminación y purga de inmersiones y usuarios.

Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

Espero que este formato sea más útil. Si necesitas más ayuda, estoy aquí para asistirte.

## Futuras mejoras
- Cambiar el nombre de una inmersión cuando ya se ha publicado.
- No permitir que un buceador se apunte a una inmersión si queda muy poco tiempo (Se podrá configurar esa duración).
- Envío de correos electrónicos de confirmación.
- Gestión de Bonos de inmersiones.

Este bot está en versión Beta 2, es funcional, pero se esperan futuras mejoras y correcciones.
