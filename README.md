
# DivingEvents Beta2

Support on Telegram @t850model102

Bot de Telegram para gestionar inmersiones de un club de buceo.

Se agradece cualquier idea o aportación.
Se puede probar el funcionamiento en el siguiente grupo privado. Solamente hay que poner el símbolo "/" o pinchar en el icono de comandos y se mostrarán los comandos disponibles.
https://t.me/+2yurjF0IprU0Y2E0

En esta versión los administradores del grupo, son los administradores del bot.

Si intentas añadir el bot a tu grupo, no funcionará. Tendrás que crear tu propio bot con el código fuente de esta página y asignar el ID de tu Grupo en las variables de tu SO.
Si necesitas ayuda profesional para implantarlo en tu grupo de telegram, puedes contactar conmigo en privado por Telegram: @t850model102



## Ver inmersiones

Para ver un resumen de todas las inmersiones. Muy útil para anclarlo en el grupo

```bash
  /ver
```
## Apuntarse a una inmersión
Muestra una lista de todas las inmersiones disponibles, incluyendo los usuarios registrados y el número de plazas restantes. Se muestra un botón con el icono de un buceador para apuntarse a la inmersión.

```bash
  /inmersiones
```
## Darse de baja en una inmersión
Permite a un usuario darse de baja de una inmersión. El bot muestra botones con las inmersiones en las que el usuario está inscrito, permitiendo elegir de cuál darse de baja.

```bash
  /baja
```
## Necesito alquilar equipo
Permite a los usuarios informar que necesitan equipo para una inmersión específica. El usuario verá botones con las inmersiones en las que está inscrito y puede seleccionar la inmersión para registrar la observación “Necesita equipo”.

```bash
  /alquilerequipo
```

## COMANDOS DE ADMINISTRADORES

## Crear una nueva inmersión
/crear_inmersion  : Crea una nueva inmersión con el nombre especificado y con un número determinado de plazas.

```bash
  /crear_inmersion <nombre> <número de plazas>
```
## Detalles de la inmersión y buceadores
Similar al comando /inmersiones, mostrando información más detallada útil para los administradores.

```bash
  /inmersiones_detalles
```
## Añadir Anotaciones
Muestra una lista de inmersiones. Al seleccionar una inmersión, se muestra una lista de usuarios inscritos. Al seleccionar un usuario, se le pedirá al administrador que escriba una observación. Muy útil para anotar que necesita equipo, que está haciendo un curso, etc...

```bash
  /observaciones
```
## Eliminar buceador de una inmersión
Elimina a un buceador específico de una inmersión. Esto no impide que el buceador se apunte de nuevo. Se mejorará en una futura correción con "listas negras".

```bash
  /eliminar_buceador
```
## Purgar datos
Purga todos los datos de inmersiones, usuarios y observaciones del sistema. Útil si tenemos inmersiones semanales y no queremos llenar los registros de inmersiones. En este caso, finalizadas las inmersiones, purgaríamos los datos.

```bash
  /purgar_datos
```

## Autor

Rubén García - [@t850model102](@t850model102)



[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

