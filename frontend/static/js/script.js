/**
 * Client Booking Page - Main JavaScript
 */

// Global state
let currentDate = new Date();
let selectedSlot = null;
let services = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadServices();
    updateDateDisplay();
    loadAvailableSlots();
    setupEventListeners();
});

/**
 * Setup Event Listeners
 */
function setupEventListeners() {
    // Date navigation
    document.getElementById('prevDay').addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() - 1);
        updateDateDisplay();
        loadAvailableSlots();
    });

    document.getElementById('nextDay').addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() + 1);
        updateDateDisplay();
        loadAvailableSlots();
    });

    // Booking form
    document.getElementById('confirmBooking').addEventListener('click', confirmBooking);
    
    // Recurrence selection
    document.getElementById('recurrenceSelect').addEventListener('change', function() {
        const recurrenceEndGroup = document.getElementById('recurrenceEndGroup');
        if (this.value !== 'none') {
            recurrenceEndGroup.style.display = 'block';
            document.getElementById('recurrenceEnd').required = true;
        } else {
            recurrenceEndGroup.style.display = 'none';
            document.getElementById('recurrenceEnd').required = false;
        }
    });
}

/**
 * Update Date Display
 */
function updateDateDisplay() {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = currentDate.toLocaleDateString('es-ES', options);
    document.getElementById('currentDate').textContent = dateString;
}

/**
 * Load Services
 */
async function loadServices() {
    try {
        const response = await fetch('/api/services');
        const data = await response.json();
        
        if (data.success) {
            services = data.services;
            populateServiceSelect();
        }
    } catch (error) {
        console.error('Error loading services:', error);
        showError('Error al cargar los servicios');
    }
}

/**
 * Populate Service Select
 */
function populateServiceSelect() {
    const select = document.getElementById('serviceSelect');
    select.innerHTML = '<option value="">Selecciona un servicio</option>';
    
    services.forEach(service => {
        const option = document.createElement('option');
        option.value = service.id;
        option.textContent = `${service.name} (${service.duration} min - $${service.price})`;
        select.appendChild(option);
    });
}

/**
 * Load Available Slots for Current Date
 */
async function loadAvailableSlots() {
    const container = document.getElementById('timeSlotsContainer');
    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
    
    try {
        const dateString = formatDate(currentDate);
        const response = await fetch(`/api/available-slots/${dateString}`);
        const data = await response.json();
        
        if (data.success) {
            displayTimeSlots(data.slots);
        } else {
            container.innerHTML = `
                <div class="alert alert-warning">
                    No hay disponibilidad para esta fecha
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading slots:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                Error al cargar los horarios disponibles
            </div>
        `;
    }
}

/**
 * Display Time Slots
 */
function displayTimeSlots(slots) {
    const container = document.getElementById('timeSlotsContainer');
    
    if (slots.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                No hay horarios disponibles para esta fecha
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    slots.forEach((slot, index) => {
        const slotElement = document.createElement('div');
        slotElement.className = `time-slot ${slot.available ? 'available' : 'occupied'} stagger-item`;
        slotElement.style.animationDelay = `${index * 0.05}s`;
        slotElement.innerHTML = `
            <i class="bi bi-clock"></i><br>
            ${slot.time}
        `;
        
        if (slot.available) {
            slotElement.addEventListener('click', () => selectTimeSlot(slot.time));
        }
        
        container.appendChild(slotElement);
    });
}

/**
 * Select Time Slot
 */
function selectTimeSlot(time) {
    selectedSlot = time;
    
    // Update UI
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
    });
    
    event.target.closest('.time-slot').classList.add('selected');
    
    // Show booking modal
    const dateString = currentDate.toLocaleDateString('es-ES', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    document.getElementById('modalDateTime').textContent = `${dateString} a las ${time}`;
    
    // Set minimum date for recurrence end
    const tomorrow = new Date(currentDate);
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('recurrenceEnd').min = formatDate(tomorrow);
    
    const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
    modal.show();
}

/**
 * Confirm Booking
 */
async function confirmBooking() {
    const form = document.getElementById('bookingForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const bookingData = {
        date: formatDate(currentDate),
        time: selectedSlot,
        client: document.getElementById('clientName').value.trim(),
        phone: document.getElementById('clientPhone').value.trim(),
        service_id: parseInt(document.getElementById('serviceSelect').value),
        recurrence: document.getElementById('recurrenceSelect').value,
        recurrence_end: document.getElementById('recurrenceEnd').value || null,
        notes: document.getElementById('appointmentNotes').value.trim()
    };
    
    // Disable button while processing
    const button = document.getElementById('confirmBooking');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
    
    try {
        const response = await fetch('/api/appointments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookingData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Close booking modal
            const bookingModal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
            bookingModal.hide();
            
            // Reset form
            form.reset();
            
            // Show success modal
            showSuccessModal(bookingData);
            
            // Reload slots
            loadAvailableSlots();
        } else {
            showError(data.error || 'Error al crear la cita');
        }
    } catch (error) {
        console.error('Error creating appointment:', error);
        showError('Error al conectar con el servidor');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-check-circle"></i> Confirmar Cita';
    }
}

/**
 * Show Success Modal
 */
function showSuccessModal(bookingData) {
    const message = document.getElementById('successMessage');
    
    if (bookingData.recurrence !== 'none') {
        message.textContent = 'Tu cita recurrente ha sido reservada exitosamente. Recibirás confirmación en tu correo.';
    } else {
        message.textContent = 'Tu cita ha sido reservada exitosamente. Recibirás confirmación en tu correo.';
    }
    
    const modal = new bootstrap.Modal(document.getElementById('successModal'));
    modal.show();
}

/**
 * Show Error Message
 */
function showError(message) {
    // Create alert
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Format Date to YYYY-MM-DD
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}
