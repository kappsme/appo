# 📅 APPO - Appointment Booking Application

Una aplicación web moderna y completa para agendamiento de citas con panel de administración, notificaciones por correo y gestión avanzada de disponibilidad.

## ✨ Características

- 📅 **Calendario Interactivo:** Sistema día a día con navegación intuitiva
- ⏰ **Horarios Flexibles:** Configuración personalizada por día de la semana
- 🔄 **Citas Recurrentes:** Soporte para citas semanales y mensuales
- 📧 **Notificaciones:** Sistema automático de confirmación por correo
- 📱 **Responsive Design:** Optimizado para dispositivos móviles y táctiles
- 🎨 **Interfaz Moderna:** Bootstrap 5.3 con animaciones fluidas
- 🎚️ **Controles Avanzados:** noUiSlider para gestión táctil de horarios
- 🐳 **Fácil Deploy:** Configuración completa con Docker Compose
- 🔒 **Validaciones:** Sistema robusto de prevención de conflictos
- 📊 **Panel Admin:** Gestión completa de servicios, horarios y citas

## 🛠️ Stack Tecnológico

- **Backend:** Flask 3.0.3 + Python 3.13 + SQLAlchemy
- **Frontend:** Bootstrap 5.3 + JavaScript Vanilla + noUiSlider
- **Base de Datos:** MySQL 5.7.40
- **Deploy:** Docker + Docker Compose
- **Emails:** Flask-Mail (configurable con SMTP)

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Puerto 5000 disponible (Flask)
- Puerto 3306 disponible (MySQL)

## 🚀 Instalación y Ejecución

### 1. Clonar el Repositorio
```bash
git clone https://github.com/kappsme/appo.git
cd appo
```

### 2. Configurar Variables de Entorno (Opcional)
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
# IMPORTANTE: Cambia las contraseñas y SECRET_KEY antes de usar en producción
nano .env
```

**⚠️ IMPORTANTE:** Para uso en producción, asegúrate de:
- Cambiar `SECRET_KEY` por una clave aleatoria y segura
- Usar contraseñas fuertes para MySQL (`DB_PASSWORD` y `MYSQL_ROOT_PASSWORD`)
- Configurar `FLASK_ENV=production` y `DEBUG=False`

### 3. Iniciar con Docker Compose
```bash
# Construir e iniciar servicios
docker compose up --build

# O en modo detached (segundo plano)
docker compose up -d --build
```

El sistema se iniciará automáticamente y:
- Creará la base de datos
- Inicializará las tablas
- Cargará datos de ejemplo (servicios y horarios por defecto)
- Estará listo para usar en http://localhost:5000

### 4. Acceder a la Aplicación

- **Cliente (Reservar Citas):** http://localhost:5000/
- **Panel Admin:** http://localhost:5000/admin

## 📱 Estructura del Proyecto

```
appo/
├── backend/
│   ├── app.py                      # Aplicación Flask principal
│   ├── models.py                   # Modelos SQLAlchemy (BD)
│   ├── config.py                   # Configuración
│   ├── init_db.py                  # Script de inicialización BD
│   ├── requirements.txt            # Dependencias Python
│   ├── Dockerfile                  # Imagen Docker backend
│   └── utils/
│       ├── validators.py           # Validaciones
│       ├── email_service.py        # Servicio de correos
│       └── recurrence.py           # Lógica de recurrencia
│
├── frontend/
│   ├── templates/
│   │   ├── base.html               # Plantilla base
│   │   ├── index.html              # Página cliente
│   │   ├── admin.html              # Panel administrador
│   │   └── 404.html                # Página error
│   └── static/
│       ├── css/
│       │   ├── styles.css          # Estilos principales
│       │   ├── animations.css      # Animaciones
│       │   └── admin.css           # Estilos admin
│       └── js/
│           ├── script.js           # Lógica cliente
│           └── admin.js            # Lógica admin
│
├── docker-compose.yml              # Orquestación de servicios
├── .env.example                    # Variables de entorno ejemplo
├── .gitignore                      # Archivos a ignorar
└── README.md                       # Documentación
```

## 🎯 Guía de Uso

### Para Clientes

1. **Seleccionar Fecha:** Usa los botones de navegación para elegir un día
2. **Elegir Horario:** Haz clic en un slot disponible (verde)
3. **Completar Información:**
   - Nombre completo
   - Teléfono
   - Selecciona un servicio
   - Opcional: Configura recurrencia (semanal/mensual)
   - Opcional: Agrega notas
4. **Confirmar Cita:** Revisa los datos y confirma
5. **Recibir Confirmación:** El sistema registra la cita

### Para Administrador

#### Gestión de Citas
- **Ver Citas:** Lista completa de todas las citas
- **Filtrar:** Por fecha y estado (activas/canceladas/completadas)
- **Ver Detalles:** Click en el botón 👁️ para ver información completa
- **Cancelar:** Click en el botón ❌ para cancelar una cita

#### Gestión de Servicios
- **Crear Servicio:** Click en "Nuevo Servicio"
  - Nombre del servicio
  - Descripción
  - Duración (minutos)
  - Precio
  - Estado (activo/inactivo)
- **Editar:** Click en el botón ✏️
- **Eliminar:** Click en el botón 🗑️ (desactiva el servicio)

#### Configuración de Disponibilidad
- **Agregar Disponibilidad:** Click en "Agregar Disponibilidad"
  - Selecciona día de la semana
  - Usa el slider para definir horario de inicio y fin
  - Define duración de cada cita
  - Habilita/deshabilita el día
- **Editar:** Click en "Editar" en cada día
- **Eliminar:** Click en botón de eliminar

## 🔧 Configuración

### Variables de Entorno

Las siguientes variables pueden configurarse en `.env`:

```bash
# Flask
FLASK_ENV=development          # production en producción
SECRET_KEY=tu-clave-secreta   # Cambiar en producción
DEBUG=True

# Base de Datos
DB_HOST=db
DB_PORT=3306
DB_NAME=appointments_db
DB_USER=appo_user
DB_PASSWORD=appo_password

# Email (Opcional - para notificaciones)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_app_password
MAIL_DEFAULT_SENDER=noreply@appo.com
```

### Configurar Notificaciones por Correo

Para habilitar las notificaciones por email:

1. Configura un servidor SMTP (ej: Gmail con contraseña de aplicación)
2. Edita las variables en `.env` o `backend/config.py`
3. Descomenta el código de envío en `backend/utils/email_service.py`

**Nota:** Por defecto, los emails se registran en logs sin enviarse.

## 📊 Modelos de Datos

### Appointment (Cita)
- `id`: ID único
- `date`: Fecha de la cita
- `time`: Hora de la cita
- `client`: Nombre del cliente
- `phone`: Teléfono del cliente
- `service_id`: ID del servicio
- `recurrence`: Tipo (none/weekly/monthly)
- `recurrence_end`: Fecha fin de recurrencia
- `parent_appointment_id`: ID de cita padre (para recurrentes)
- `status`: Estado (active/cancelled/completed)
- `notes`: Notas adicionales
- `created_at`: Fecha de creación
- `updated_at`: Fecha de actualización

### Service (Servicio)
- `id`: ID único
- `name`: Nombre del servicio
- `description`: Descripción
- `duration`: Duración en minutos
- `price`: Precio del servicio
- `active`: Activo/inactivo
- `created_at`: Fecha de creación

### Availability (Disponibilidad)
- `id`: ID único
- `day_of_week`: Día de la semana (0-6)
- `start_time`: Hora de inicio
- `end_time`: Hora de fin
- `duration_minutes`: Duración de cada cita
- `enabled`: Habilitado/deshabilitado
- `created_at`: Fecha de creación

### RecurrenceRule (Reglas de Recurrencia)
- `id`: ID único
- `appointment_id`: ID de la cita
- `frequency`: Frecuencia (daily/weekly/monthly)
- `interval`: Intervalo
- `count`: Número de ocurrencias
- `until`: Fecha de finalización
- `by_day`: Días específicos
- `created_at`: Fecha de creación

## 🔐 Seguridad

- ✅ Validación de datos en frontend y backend
- ✅ Prevención de conflictos de horarios
- ✅ Sanitización de inputs
- ✅ Validación de números de teléfono
- ✅ Verificación de disponibilidad antes de confirmar
- ✅ Protección contra duplicados

## 📧 Notificaciones

El sistema soporta envío de correos para:
- ✅ Confirmación de cita reservada
- ✅ Recordatorio 24h antes (requiere configuración adicional)
- ✅ Confirmación de cancelación
- ✅ Notificación de cambios (admin)

## 🐳 Comandos Docker Útiles

```bash
# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f web

# Ver logs de base de datos
docker compose logs -f db

# Detener servicios
docker compose down

# Detener y eliminar volúmenes (reinicio completo)
docker compose down -v

# Reconstruir contenedores
docker compose up --build

# Acceder a shell del contenedor web
docker compose exec web bash

# Acceder a MySQL
docker compose exec db mysql -u appo_user -p appointments_db
# Password: appo_password

# Ejecutar comandos en el contenedor
docker compose exec web python init_db.py
```

## 🧪 Desarrollo Local (sin Docker)

Si prefieres ejecutar sin Docker:

```bash
# 1. Instalar dependencias
cd backend
pip install -r requirements.txt

# 2. Configurar base de datos MySQL
# Crear base de datos 'appointments_db'

# 3. Configurar variables de entorno
export DB_HOST=localhost
export DB_USER=tu_usuario
export DB_PASSWORD=tu_password

# 4. Inicializar base de datos
python init_db.py

# 5. Ejecutar aplicación
flask run

# La aplicación estará en http://localhost:5000
```

## 🚀 Despliegue en Producción

Para despliegue en producción:

1. **Cambiar configuraciones de seguridad:**
   ```bash
   FLASK_ENV=production
   DEBUG=False
   SECRET_KEY=clave-secreta-aleatoria-muy-larga
   ```

2. **Usar contraseñas seguras para MySQL**

3. **Configurar SMTP real** para notificaciones

4. **Usar proxy inverso** (nginx) con SSL/HTTPS

5. **Configurar backups automáticos** de la base de datos

6. **Considerar uso de:** Gunicorn + nginx para producción

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🐛 Reporte de Problemas

Para reportar problemas o solicitar nuevas características, por favor crea un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## 👥 Autor

**kappsme** - [GitHub](https://github.com/kappsme)

## 🙏 Agradecimientos

- Bootstrap por el framework CSS
- Flask por el framework web
- noUiSlider por los controles de rango avanzados
- La comunidad open source

---

**⭐ Si te gusta este proyecto, por favor dale una estrella en GitHub! ⭐**
