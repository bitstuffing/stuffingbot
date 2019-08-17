Actualmente se encuentra en desarrollo, pero era un TODO que había que terminar

Este bot está implementado para funcionar sobre una rasberrypi (raspbian), pero
la idea es que sea totalmente portable y pueda funcionar de manera modular
en muchas más plataformas, incluídas las más livianas.

Está construído en python2, no se mantiene la compatibilidad con python3 debido
a que el módulo de alfa (kodi) está implementado en python2 y es muy costoso
de "compatibilizar"

Necesitas editar el archivo configuration.json en el que se encuentran las rutas,
usuarios y las keys privadas de las apis; además de otras configuraciones.

Utiliza como dependencia externa (addon de kodi) el addon alfa para descargar
de diferentes lugares, más información: https://github.com/alfa-addon/addon/.
Pero se puede resumir que lo que hace es un pequeño "hack" para sustituir
todas las partes que utiliza como dependencias de kodi y funcionar sobre python2
