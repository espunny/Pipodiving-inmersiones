
# DivingEvents Beta v4 (Versión MultiGrupo)

Support on Telegram @t850model102

Bot de Telegram para gestionar inmersiones de un club de buceo.

Se agradece cualquier idea o aportación.
Se puede probar el funcionamiento en el siguiente grupo privado. Solamente hay que poner el símbolo "/" o pinchar en el icono de comandos y se mostrarán los comandos disponibles.
https://t.me/+2yurjF0IprU0Y2E0


Cambios versión beta4:
- Se ha solucionado un bug por el que los propietarios de un grupo, no tienen los permisos de los administradores.
- Se ha solucionado un bug por el que los * en el nombre de las inmersiones, interferían con el Markdown de Telegram.
- Se ha eliminado la posiblidad de que varios grupos tengas sus inmersiones separadas.
- Ahora Un club con varios grupos, puede gestionar las mismas inmersiones, siempre que estén en la lista blanca de grupos.

Mejoras de la versión beta3:
- Consultas asíncronas a la base de datos.
- Se crean dos plazas de reserva con cada inmersión.
- El mismo Bot, podrá funcionar en varios grupos simultáneamente. Por motivos de rendimiento y seguridad aún hay una lista blanca de grupos en la variable de entorno: AUTHORIZED_GROUP_ID. El administrador que quiera instalar el bot en un grupo no autorizado tendrá que solicitarlo con un mensaje.
- Se ha añadido un timestamp en las inmersiones para poder purgar la base de datos después de un tiempo. Necesario para que no queden inmeriones huérfanas u olvidadas en la base de datos.
- Ahora los mensajes de interacción con el bot, se envían en silencio para no molestar al resto de integrantes.
- El comando /ver ahora se ancla al ejecutarse.
- La creación de inmersiones, las bajas, altas de buceadores y bajas de los mismos, actualizarán el comando /ver automáticamente, anclando la lista de inmersiones actualizada.

Mejoras de la versión Beta2:
- En esta versión los administradores del grupo, son los administradores del bot.
- Todos los comandos ahora son interactivos excepto eliminar buceador.
- Versión con persistencia en bases de datos.


--------
Telegram bot to manage dives of a diving club.
This is a preliminary version.

Contributions are welcome.
You can test the operation in the following private group.
[https://t.me/+pAmFphtBgNo5MDU8](https://t.me/+pAmFphtBgNo5MDU8)

# Bot de Gestión de Inmersiones

Este bot está diseñado para gestionar inmersiones y usuarios registrados en ellas. Permite a los usuarios ver las inmersiones disponibles, registrarse en ellas, añadir observaciones, y más. Algunas funciones son exclusivas para administradores.

## Comandos Disponibles

### Comandos Generales

1. **`/start`**
   - **Descripción**: Inicia el bot y muestra un mensaje de bienvenida con el `chat_id` del grupo autorizado.
   - **Uso**: Simplemente escribe `/start` en el chat.

2. **`/inmersiones`**
   - **Descripción**: Muestra una lista de todas las inmersiones disponibles, incluyendo los usuarios registrados y el número de plazas restantes.
   - **Uso**: `/inmersiones`
   - **Ejemplo**:
     ```
     /inmersiones
     ```
3. **`/baja`**
   - **Descripción**: Permite darse de baja de una inmersión.
   - **Uso**: `/baja`
   - **Ejemplo**:
     ```
     /baja
     ```
4. **`/alquilerequipo`**
   - **Descripción**: Permite indicar que necesitamos alquilar equipo.
   - **Uso**: `/alquilerequipo`
   - **Ejemplo**:
     ```
     /alquilerequipo
     ```
### Comandos para Administradores
**Nota**: Estos comandos solo pueden ser ejecutados por administradores.

1. **`/inmersiones_detalles`**
   - **Descripción**: Muestra detalles adicionales de las inmersiones, incluyendo observaciones si existen.
   - **Uso**: `/inmersiones_detalles`
   - **Ejemplo**:
     ```
     /inmersiones_detalles
     ```

2. **`/crear_inmersion <ID del evento> <Nombre del evento> <Plazas>`**
   - **Descripción**: Crea una nueva inmersión con el ID y nombre especificados, y con un número determinado de plazas.
   - **Uso**: `/crear_inmersion <ID del evento> <Nombre del evento> <Plazas>`
   - **Ejemplo**:
     ```
     /crear_inmersion 123 Sábado 9:30 -Open Water 12
     ```

3. **`/borrar_inmersion <ID del evento>`**
   - **Descripción**: Elimina una inmersión específica.
   - **Uso**: `/borrar_inmersion <ID del evento>`
   - **Ejemplo**:
     ```
     /borrar_inmersion 123
     ```

4. **`/observaciones <ID del evento> <ID del usuario> <Observaciones>`**
   - **Descripción**: Añade una observación para un usuario específico en una inmersión específica.
   - **Uso**: `/observaciones <ID del evento> <ID del usuario> <Observaciones>`
   - **Ejemplo**:
     ```
     /observaciones 123 456 Curso OWD. Necesita equipo
     ```

5. **`/eliminar_buceador <ID del evento> <ID del usuario>`**
   - **Descripción**: Elimina a un usuario específico de una inmersión.
   - **Uso**: `/eliminar_usuario <ID del evento> <ID del usuario>`
   - **Ejemplo**:
     ```
     /eliminar_buceador 123 456
     ```

6. **`/purgar_datos`**
   - **Descripción**: Purga todas las inmersiones y observaciones del sistema.
   - **Uso**: `/purgar_datos`
   - **Ejemplo**:
     ```
     /purgar_datos
     ```

## Autor

Rubén García - [@t850model102](@t850model102)



[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

