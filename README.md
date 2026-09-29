# Liga Duolingo Familiar - versión manual

Aplicación web manual para una liga familiar de Duolingo.

## Accesos
- **Familia:** la página principal es de solo lectura. Puede consultar ranking, XP, multas, premios, puntos acumulados e histórico.
- **Administrador:** el botón **Administrador** permite iniciar sesión y habilita la edición manual de XP/multas y el cierre semanal.

## Configuración del administrador
Antes de publicar la app, define estas variables de entorno:
- `ADMIN_PASSWORD`: contraseña privada del administrador.
- `SECRET_KEY`: cadena larga y aleatoria para proteger la sesión.

No compartas `ADMIN_PASSWORD` con los participantes.

## Funcionamiento
- Semana: lunes 12:01 a. m. a domingo 10:00 p. m., hora de Colombia.
- XP y multas se ingresan manualmente.
- XP efectivos = max(0, XP - multa).
- Premios: 50.000 / 40.000 / 30.000 / 20.000 / 10.000 puntos para los cinco primeros.
- Al cerrar la semana, los premios se suman al acumulado, se guarda el histórico y XP/multas vuelven a cero.
- No incluye sincronización automática con Duolingo.

## Ejecución local
1. Instala dependencias: `pip install -r requirements.txt`
2. Define `ADMIN_PASSWORD` y `SECRET_KEY`.
3. Ejecuta: `python app.py`
4. Abre `http://localhost:8000`
