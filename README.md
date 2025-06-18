# Grabadora Evolutiva

Este proyecto permite grabar audio desde el navegador y lleva un registro de cada acción realizada. Incluye herramientas de diagnóstico y un pequeño historial visible desde la interfaz.

## Estructura de carpetas
- **logs/**: archivos de registro. `actividad.log`, `mejoras_sugeridas.log` y varias listas JSON de sugerencias. Se incluye un `.keep` para conservar la carpeta en git.
- **control/**: archivos de seguimiento del proyecto (`rutas.txt`, `agentes.txt`, `bitacora.txt`).
- **static/**: archivos estáticos como el script del frontend.
- **templates/**: plantillas HTML de la aplicación.

## Registro y visualización de actividad
- Cada botón de la interfaz (grabar, detener, reproducir) envía un evento al backend mediante `/registrar`.
- Los eventos se guardan en `logs/actividad.log` con fecha y hora.
- El botón **Ver historial** abre `/historial`, donde se muestran todas las acciones registradas. Si el archivo está vacío se indica en pantalla.
- Desde `/admin` se pueden revisar todos los archivos de la carpeta `logs` mediante botones que muestran su contenido.

## Administración de logs
La sección `/admin` permite visualizar en pantalla el contenido de todos los archivos de registro.

## Compatibilidad de audio
El script intenta usar el formato de audio más compatible (WebM, MP4 o WAV). En navegadores Safari/iOS se probará MP4. Si ninguno está disponible, se mostrará un mensaje de incompatibilidad.

## Pruebas automatizadas
Se incluye una prueba básica con **pytest** que verifica que el endpoint `/registrar` escriba correctamente en `actividad.log`.

Para ejecutar las pruebas:
```bash
pip install -r requirements.txt
pytest
```

## Limitaciones conocidas
En algunos dispositivos iOS la grabación de audio puede no estar soportada pese al ajuste de formato. Si ocurre, la aplicación mostrará un aviso y no iniciará la grabación.

## Informe Evolutivo
Para detalles y contexto adicional del proyecto puede consultarse el **Evolutive Report June 2025** (no incluido en este repositorio).

