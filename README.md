Support on Telegram @t850model102

Bot de Telegram para gestionar inmersiones de un club de buceo.
Esta es una versión preliminar.

Se agradece cualquier idea o aportación.
Se puede probar el funcionamiento en el siguiente grupo privado (Se requiere verificación).
https://t.me/+-1Yp622bPi5iMDc0

--------
Telegram bot to manage dives of a diving club.
This is a preliminary version.

Contributions are welcome.
You can test the operation in the following private group (Verification required).
https://t.me/+-1Yp622bPi5iMDc0

# Bot de Gestión de Inmersiones

Este bot está diseñado para gestionar inmersiones y usuarios registrados en ellas. Permite a los usuarios ver las inmersiones disponibles, registrarse en ellas, añadir observaciones, y más. Algunas funciones son exclusivas para administradores.

## Comandos Disponibles

### Comandos Generales

¡¡ADVERTENCIA. ACTUALMENTE NO SE PUEDEN USAR ESPACIOS EN LOS COMANDOS!!

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
     /crear_inmersion 123 "09:20-Sábado-Advanced" 12
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
     /observaciones 123 456 "CursoOW-Necesita_equipo"
     ```

5. **`/eliminar_usuario <ID del evento> <ID del usuario>`**
   - **Descripción**: Elimina a un usuario específico de una inmersión.
   - **Uso**: `/eliminar_usuario <ID del evento> <ID del usuario>`
   - **Ejemplo**:
     ```
     /eliminar_usuario 123 456
     ```

6. **`/purgar_datos`**
   - **Descripción**: Purga todas las inmersiones y observaciones del sistema.
   - **Uso**: `/purgar_datos`
   - **Ejemplo**:
     ```
     /purgar_datos
     ```

## Notas Adicionales

- El bot verifica que el `chat_id` del grupo coincida con el autorizado para evitar usos no autorizados.
- Asegúrate de que los comandos que requieran parámetros se utilicen con el formato adecuado para evitar errores.

Este bot está en versión Alpha 1.3, y se esperan futuras mejoras y correcciones.
