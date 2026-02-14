# 📅 APPO - Appointment Booking Application

Una aplicación web moderna para agendamiento de citas con panel de administración, notificaciones por correo y gestión avanzada de disponibilidad.

## ✨ Características

- 📅 Calendario interactivo día a día
- ⏰ Configuración flexible de horarios y duración de citas
- 🔄 Citas recurrentes (semanal/mensual)
- 📧 Notificaciones automáticas por correo
- 📱 Diseño completamente responsive
- 🎨 Interfaz moderna con Bootstrap 5.3
- ✨ Animaciones fluidas y transiciones
- 🐳 Deploy fácil con Docker
- 🔒 Validaciones robustas
- 📊 Panel de administración intuitivo

## 🛠️ Stack Tecnológico

- **Backend:** Flask 3.0.3 + Python 3.13
- **Frontend:** Bootstrap 5.3 + JavaScript Vanilla
- **Base de Datos:** MySQL 5.7.40
- **Deploy:** Docker + Docker Compose
- **Emails:** Flask-Mail + SMTP

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

### 2. Iniciar con Docker Compose
```bash
docker-compose up -d
```

### 3. Crear Base de Datos (primera vez)
```bash
docker-compose exec web python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 4. Acceder a la Aplicación

- **Cliente (Reservar Citas):** http://localhost:5000/
- **Panel Admin:** http://localhost:5000/admin

## 📱 Estructura del Proyecto

``` 
appo/
├── backend/
│   ├── app.py                 # Aplicación Flask principal
│   ├── models.py              # Modelos de BD (SQLAlchemy)
│   ├── config.py              # Configuración
│   ├── email_service.py       # Servicio de notificaciones
│   ├── validators.py          # Validaciones personalizadas
│   ├── requirements.txt        # Dependencias Python
│   ├── Dockerfile             # Imagen Docker
│   └── init_db.py             # Script inicialización BD
│
├── frontend/
│   ├── templates/
│   │   ├── base.html          # Plantilla base
│   │   ├── index.html         # Página cliente
│   │   ├── admin.html         # Panel administrador
│   │   └── 404.html           # Página error
│   │
│   └── static/
│       ├── css/
│       │   ├── styles.css     # Estilos principales
│       │   └── animations.css # Animaciones
│       │
│       └── js/
│           ├── script.js      # Lógica cliente
│           ├── admin.js       # Lógica admin
│           └── utils.js       # Funciones utilitarias
│
└── docker-compose.yml         # Configuración Docker
```

## 🎯 Guía de Uso

### Para Clientes

1. Selecciona una fecha en el calendario
2. Elige un horario disponible
3. Completa tu información (nombre, teléfono, servicio)
4. Confirma tu cita en el modal
5. Recibe confirmación por correo

### Para Administrador

1. Accede a `/admin`
2. **Horarios:** Define disponibilidad por día de la semana
3. **Servicios:** Crea y gestiona servicios ofrecidos
4. **Citas:** Visualiza, modifica o cancela citas
5. **Reportes:** Ve estadísticas y ocupación

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en raíz (opcional):

```
FLASK_ENV=production
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password
MAIL_DEFAULT_SENDER=noreply@appo.com
```

### Configurar Correos

Editar `backend/config.py`:

```python
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "tu_email@gmail.com"
MAIL_PASSWORD = "tu_contraseña_app"
```

## 📊 Modelos de Datos

### Appointment (Cita)
- `id`: ID único
- `date`: Fecha
- `time`: Hora
- `client`: Nombre cliente
- `phone`: Teléfono
- `service_id`: ID servicio
- `recurrence`: Tipo (none/weekly/monthly)
- `recurrence_end`: Fecha fin recurrencia
- `created_at`: Timestamp creación
- `status`: active/cancelled

### Availability (Disponibilidad)
- `id`: ID único
- `day_of_week`: Día semana (0-6)
- `start_time`: Hora inicio
- `end_time`: Hora fin
- `duration_minutes`: Duración cita
- `enabled`: Habilitado/deshabilitado

### Service (Servicio)
- `id`: ID único
- `name`: Nombre servicio
- `description`: Descripción
- `duration`: Duración por defecto
- `price`: Precio (opcional)
- `active`: Activo/inactivo

## 🔐 Seguridad

- Validación de datos en frontend y backend
- Prevención de conflictos de horarios
- Sanitización de inputs
- Headers de seguridad CSRF
- Rate limiting en API (opcional)

## 📧 Notificaciones

Se envían correos automáticos para:
- ✅ Confirmación de cita reservada
- ✅ Recordatorio 24h antes
- ✅ Confirmación de cancelación
- ✅ Cambios en horarios (admin)

## 🐳 Comandos Docker

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Detener servicios
docker-compose down

# Recrear base de datos
docker-compose down -v
docker-compose up -d

# Acceder a shell de BD
docker-compose exec db mysql -u appo_user -p appointments_db
```

## 🚀 Despliegue en Producción

1. Cambiar `FLASK_ENV` a `production`
2. Generar `SECRET_KEY` seguro
3. Configurar SMTP válido
4. Usar reverse proxy (nginx)
5. Configurar SSL/HTTPS
6. Backup automático de BD

## 📞 Soporte

Para reportar problemas, crear un issue en el repositorio.

## 📄 Licencia

MIT License - Ver archivo LICENSE
