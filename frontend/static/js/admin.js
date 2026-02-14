/**
 * Admin Panel - Main JavaScript
 */

// Global state
let currentAppointments = [];
let currentServices = [];
let currentAvailability = [];
let editingServiceId = null;
let editingAvailabilityId = null;

// Day names in Spanish
const dayNames = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
    setupEventListeners();
});

/**
 * Initialize Admin Panel
 */
function initializeAdmin() {
    loadAppointments();
    loadServices();
    loadAvailability();
    setupTimeSlider();
}

/**
 * Setup Event Listeners
 */
function setupEventListeners() {
    // Appointments
    document.getElementById('refreshAppointments').addEventListener('click', loadAppointments);
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    
    // Services
    document.getElementById('saveService').addEventListener('click', saveService);
    
    // Availability
    document.getElementById('saveAvailability').addEventListener('click', saveAvailability);
    
    // Tab changes
    document.querySelectorAll('#adminTabs button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const targetTab = e.target.getAttribute('data-bs-target');
            if (targetTab === '#appointments') {
                loadAppointments();
            } else if (targetTab === '#services') {
                loadServices();
            } else if (targetTab === '#availability') {
                loadAvailability();
            }
        });
    });
    
    // Reset modals on close
    document.getElementById('serviceModal').addEventListener('hidden.bs.modal', resetServiceForm);
    document.getElementById('availabilityModal').addEventListener('hidden.bs.modal', resetAvailabilityForm);
}

/**
 * Load Appointments
 */
async function loadAppointments() {
    const tbody = document.getElementById('appointmentsTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </td>
        </tr>
    `;
    
    try {
        let url = '/api/appointments?status=active';
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            currentAppointments = data.appointments;
            displayAppointments(currentAppointments);
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error al cargar las citas</td></tr>';
    }
}

/**
 * Apply Filters
 */
async function applyFilters() {
    const date = document.getElementById('filterDate').value;
    const status = document.getElementById('filterStatus').value;
    
    let url = '/api/appointments?';
    if (date) url += `date=${date}&`;
    if (status) url += `status=${status}&`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            currentAppointments = data.appointments;
            displayAppointments(currentAppointments);
        }
    } catch (error) {
        console.error('Error filtering appointments:', error);
    }
}

/**
 * Display Appointments in Table
 */
function displayAppointments(appointments) {
    const tbody = document.getElementById('appointmentsTableBody');
    
    if (appointments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No hay citas para mostrar</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    appointments.forEach(appointment => {
        const row = document.createElement('tr');
        row.className = 'fade-in';
        
        const statusClass = appointment.status === 'active' ? 'success' : 
                          appointment.status === 'cancelled' ? 'danger' : 'info';
        
        row.innerHTML = `
            <td>${appointment.date}</td>
            <td><strong>${appointment.time}</strong></td>
            <td>${appointment.client}</td>
            <td>${appointment.phone}</td>
            <td>${appointment.service_name || 'N/A'}</td>
            <td>
                <span class="badge bg-${statusClass}">${appointment.status}</span>
                ${appointment.recurrence !== 'none' ? `<span class="badge bg-info ms-1"><i class="bi bi-arrow-repeat"></i> ${appointment.recurrence}</span>` : ''}
            </td>
            <td>
                <button class="btn btn-sm btn-info action-btn" onclick="viewAppointment(${appointment.id})">
                    <i class="bi bi-eye"></i>
                </button>
                ${appointment.status === 'active' ? `
                    <button class="btn btn-sm btn-danger action-btn" onclick="cancelAppointment(${appointment.id})">
                        <i class="bi bi-x-circle"></i>
                    </button>
                ` : ''}
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * View Appointment Details
 */
async function viewAppointment(appointmentId) {
    const appointment = currentAppointments.find(a => a.id === appointmentId);
    
    if (!appointment) return;
    
    const detailsBody = document.getElementById('appointmentDetailsBody');
    detailsBody.innerHTML = `
        <div class="mb-3">
            <strong><i class="bi bi-calendar"></i> Fecha:</strong> ${appointment.date}
        </div>
        <div class="mb-3">
            <strong><i class="bi bi-clock"></i> Hora:</strong> ${appointment.time}
        </div>
        <div class="mb-3">
            <strong><i class="bi bi-person"></i> Cliente:</strong> ${appointment.client}
        </div>
        <div class="mb-3">
            <strong><i class="bi bi-telephone"></i> Teléfono:</strong> ${appointment.phone}
        </div>
        <div class="mb-3">
            <strong><i class="bi bi-briefcase"></i> Servicio:</strong> ${appointment.service_name || 'N/A'}
        </div>
        <div class="mb-3">
            <strong><i class="bi bi-arrow-repeat"></i> Recurrencia:</strong> ${appointment.recurrence}
            ${appointment.recurrence_end ? `<br><small>Hasta: ${appointment.recurrence_end}</small>` : ''}
        </div>
        <div class="mb-3">
            <strong><i class="bi bi-info-circle"></i> Estado:</strong> 
            <span class="badge bg-${appointment.status === 'active' ? 'success' : 'danger'}">${appointment.status}</span>
        </div>
        ${appointment.notes ? `
            <div class="mb-3">
                <strong><i class="bi bi-chat-left-text"></i> Notas:</strong><br>
                ${appointment.notes}
            </div>
        ` : ''}
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('appointmentDetailsModal'));
    modal.show();
}

/**
 * Cancel Appointment
 */
async function cancelAppointment(appointmentId) {
    if (!confirm('¿Estás seguro de que deseas cancelar esta cita?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/appointments/${appointmentId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Cita cancelada exitosamente');
            loadAppointments();
        } else {
            showError(data.error || 'Error al cancelar la cita');
        }
    } catch (error) {
        console.error('Error cancelling appointment:', error);
        showError('Error al conectar con el servidor');
    }
}

/**
 * Load Services
 */
async function loadServices() {
    const tbody = document.getElementById('servicesTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </td>
        </tr>
    `;
    
    try {
        const response = await fetch('/api/services');
        const data = await response.json();
        
        if (data.success) {
            currentServices = data.services;
            displayServices(currentServices);
        }
    } catch (error) {
        console.error('Error loading services:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error al cargar los servicios</td></tr>';
    }
}

/**
 * Display Services in Table
 */
function displayServices(services) {
    const tbody = document.getElementById('servicesTableBody');
    
    if (services.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay servicios configurados</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    services.forEach(service => {
        const row = document.createElement('tr');
        row.className = 'fade-in';
        
        row.innerHTML = `
            <td><strong>${service.name}</strong></td>
            <td>${service.description || '-'}</td>
            <td>${service.duration} min</td>
            <td>$${service.price.toFixed(2)}</td>
            <td>
                <span class="badge bg-${service.active ? 'success' : 'secondary'}">
                    ${service.active ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-warning action-btn" onclick="editService(${service.id})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger action-btn" onclick="deleteService(${service.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Edit Service
 */
function editService(serviceId) {
    const service = currentServices.find(s => s.id === serviceId);
    
    if (!service) return;
    
    editingServiceId = serviceId;
    
    document.getElementById('serviceId').value = service.id;
    document.getElementById('serviceName').value = service.name;
    document.getElementById('serviceDescription').value = service.description || '';
    document.getElementById('serviceDuration').value = service.duration;
    document.getElementById('servicePrice').value = service.price;
    document.getElementById('serviceActive').checked = service.active;
    
    document.getElementById('serviceModalTitle').innerHTML = '<i class="bi bi-pencil"></i> Editar Servicio';
    
    const modal = new bootstrap.Modal(document.getElementById('serviceModal'));
    modal.show();
}

/**
 * Save Service (Create or Update)
 */
async function saveService() {
    const form = document.getElementById('serviceForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const serviceData = {
        name: document.getElementById('serviceName').value.trim(),
        description: document.getElementById('serviceDescription').value.trim(),
        duration: parseInt(document.getElementById('serviceDuration').value),
        price: parseFloat(document.getElementById('servicePrice').value),
        active: document.getElementById('serviceActive').checked
    };
    
    const button = document.getElementById('saveService');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    try {
        const method = editingServiceId ? 'PUT' : 'POST';
        const url = editingServiceId ? `/api/services/${editingServiceId}` : '/api/services';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(serviceData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Servicio guardado exitosamente');
            const modal = bootstrap.Modal.getInstance(document.getElementById('serviceModal'));
            modal.hide();
            loadServices();
        } else {
            showError(data.error || 'Error al guardar el servicio');
        }
    } catch (error) {
        console.error('Error saving service:', error);
        showError('Error al conectar con el servidor');
    } finally {
        button.disabled = false;
        button.innerHTML = 'Guardar';
    }
}

/**
 * Delete Service
 */
async function deleteService(serviceId) {
    if (!confirm('¿Estás seguro de que deseas eliminar este servicio?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/services/${serviceId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Servicio eliminado exitosamente');
            loadServices();
        } else {
            showError(data.error || 'Error al eliminar el servicio');
        }
    } catch (error) {
        console.error('Error deleting service:', error);
        showError('Error al conectar con el servidor');
    }
}

/**
 * Reset Service Form
 */
function resetServiceForm() {
    editingServiceId = null;
    document.getElementById('serviceForm').reset();
    document.getElementById('serviceId').value = '';
    document.getElementById('serviceModalTitle').innerHTML = '<i class="bi bi-briefcase"></i> Nuevo Servicio';
}

/**
 * Load Availability
 */
async function loadAvailability() {
    const container = document.getElementById('availabilityContainer');
    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
    
    try {
        const response = await fetch('/api/availability');
        const data = await response.json();
        
        if (data.success) {
            currentAvailability = data.availability;
            displayAvailability(currentAvailability);
        }
    } catch (error) {
        console.error('Error loading availability:', error);
        container.innerHTML = '<div class="alert alert-danger">Error al cargar la disponibilidad</div>';
    }
}

/**
 * Display Availability
 */
function displayAvailability(availability) {
    const container = document.getElementById('availabilityContainer');
    
    if (availability.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No hay disponibilidad configurada</div>';
        return;
    }
    
    container.innerHTML = '';
    
    availability.forEach(avail => {
        const dayCard = document.createElement('div');
        dayCard.className = `availability-day ${!avail.enabled ? 'disabled' : ''} fade-in`;
        
        dayCard.innerHTML = `
            <div class="row align-items-center">
                <div class="col-md-3">
                    <h5><i class="bi bi-calendar"></i> ${dayNames[avail.day_of_week]}</h5>
                </div>
                <div class="col-md-4">
                    <div class="time-display">
                        <i class="bi bi-clock"></i> ${avail.start_time} - ${avail.end_time}
                    </div>
                    <small class="text-muted">Duración: ${avail.duration_minutes} min</small>
                </div>
                <div class="col-md-2">
                    <span class="badge bg-${avail.enabled ? 'success' : 'secondary'}">
                        ${avail.enabled ? 'Habilitado' : 'Deshabilitado'}
                    </span>
                </div>
                <div class="col-md-3 text-end">
                    <button class="btn btn-sm btn-warning action-btn" onclick="editAvailability(${avail.id})">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                    <button class="btn btn-sm btn-danger action-btn" onclick="deleteAvailability(${avail.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(dayCard);
    });
}

/**
 * Setup Time Range Slider
 */
function setupTimeSlider() {
    const slider = document.getElementById('timeRangeSlider');
    
    if (!slider || slider.noUiSlider) return;
    
    noUiSlider.create(slider, {
        start: [9 * 60, 18 * 60], // 9:00 to 18:00 in minutes
        connect: true,
        range: {
            'min': 0,
            'max': 24 * 60
        },
        step: 15,
        format: {
            to: function(value) {
                return Math.round(value);
            },
            from: function(value) {
                return Number(value);
            }
        }
    });
    
    slider.noUiSlider.on('update', function(values) {
        const startMinutes = parseInt(values[0]);
        const endMinutes = parseInt(values[1]);
        
        const startTime = minutesToTime(startMinutes);
        const endTime = minutesToTime(endMinutes);
        
        document.getElementById('startTimeDisplay').textContent = startTime;
        document.getElementById('endTimeDisplay').textContent = endTime;
        document.getElementById('startTime').value = startTime;
        document.getElementById('endTime').value = endTime;
    });
}

/**
 * Convert Minutes to Time String
 */
function minutesToTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
}

/**
 * Convert Time String to Minutes
 */
function timeToMinutes(time) {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
}

/**
 * Edit Availability
 */
function editAvailability(availabilityId) {
    const avail = currentAvailability.find(a => a.id === availabilityId);
    
    if (!avail) return;
    
    editingAvailabilityId = availabilityId;
    
    document.getElementById('availabilityId').value = avail.id;
    document.getElementById('dayOfWeek').value = avail.day_of_week;
    document.getElementById('durationMinutes').value = avail.duration_minutes;
    document.getElementById('availabilityEnabled').checked = avail.enabled;
    
    // Update slider
    const slider = document.getElementById('timeRangeSlider');
    if (slider.noUiSlider) {
        const startMinutes = timeToMinutes(avail.start_time);
        const endMinutes = timeToMinutes(avail.end_time);
        slider.noUiSlider.set([startMinutes, endMinutes]);
    }
    
    const modal = new bootstrap.Modal(document.getElementById('availabilityModal'));
    modal.show();
}

/**
 * Save Availability
 */
async function saveAvailability() {
    const form = document.getElementById('availabilityForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const availabilityData = {
        day_of_week: parseInt(document.getElementById('dayOfWeek').value),
        start_time: document.getElementById('startTime').value,
        end_time: document.getElementById('endTime').value,
        duration_minutes: parseInt(document.getElementById('durationMinutes').value),
        enabled: document.getElementById('availabilityEnabled').checked
    };
    
    const button = document.getElementById('saveAvailability');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    try {
        const method = editingAvailabilityId ? 'PUT' : 'POST';
        const url = editingAvailabilityId ? `/api/availability/${editingAvailabilityId}` : '/api/availability';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(availabilityData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Disponibilidad guardada exitosamente');
            const modal = bootstrap.Modal.getInstance(document.getElementById('availabilityModal'));
            modal.hide();
            loadAvailability();
        } else {
            showError(data.error || 'Error al guardar la disponibilidad');
        }
    } catch (error) {
        console.error('Error saving availability:', error);
        showError('Error al conectar con el servidor');
    } finally {
        button.disabled = false;
        button.innerHTML = 'Guardar';
    }
}

/**
 * Delete Availability
 */
async function deleteAvailability(availabilityId) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta disponibilidad?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/availability/${availabilityId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Disponibilidad eliminada exitosamente');
            loadAvailability();
        } else {
            showError(data.error || 'Error al eliminar la disponibilidad');
        }
    } catch (error) {
        console.error('Error deleting availability:', error);
        showError('Error al conectar con el servidor');
    }
}

/**
 * Reset Availability Form
 */
function resetAvailabilityForm() {
    editingAvailabilityId = null;
    document.getElementById('availabilityForm').reset();
    document.getElementById('availabilityId').value = '';
    
    // Reset slider
    const slider = document.getElementById('timeRangeSlider');
    if (slider.noUiSlider) {
        slider.noUiSlider.set([9 * 60, 18 * 60]);
    }
}

/**
 * Show Success Message
 */
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Show Error Message
 */
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}
