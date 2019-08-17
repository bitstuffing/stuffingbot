Actualmente se encuentra en desarrollo, pero era un TODO que había que terminar

Este bot está implementado para funcionar sobre una rasberrypi (raspbian), pero
la idea es que sea totalmente portable y pueda funcionar de manera modular
en muchas más plataformas, incluídas las más livianas.

Está construído en python, y se está migrando a python3.7
(por temas de multithread se requiere pyton3.6+ para atender a más de un usuario
 a la vez)

Necesitas crear un archivo configuration.json en el que se encuentran las rutas,
usuarios y las keys privadas de las apis.

Utiliza como dependencia externa (addon de kodi) el addon alfa para descargar
de diferentes lugares, más información: https://github.com/alfa-addon/addon/.
Pero se puede resumir que lo que hace es un pequeño "hack" para sustituir
todas las partes que utiliza como dependencias de kodi y funcionar sobre python2
