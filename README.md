## Migrar modelos a la DB
1. Inicializar Flask-Migrate
Ejecuta este comando en la terminal para iniciar la configuración de migraciones: 

flask db init

2. Crear una Migración
Cada vez que agregues o modifiques modelos, usa este comando para generar una nueva migración:

flask db migrate -m "Mensaje descriptivo"

3. Aplicar la Migración a la Base de Datos
Después de crear la migración, aplícala con:

flask db upgrade

## Opcional:
Ver el Historial de Migraciones
Para ver el historial de migraciones aplicadas:

flask db history

Para deshacer la última migración:

flask db downgrade

## Ejecutar docker
1. Construir la imagen
docker build -t turnogo .

2. Correr el contenedor
docker compose up -d
