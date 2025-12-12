// Configuración
const API_BASE_URL = 'https://localhost:3000';
let refreshInterval = null;

// Elementos del DOM
const elements = {
    currentTime: document.getElementById('current-time'),
    apiStatus: document.getElementById('api-status'),
    cpsContainer: document.getElementById('cps-container'),
    driversTableBody: document.getElementById('drivers-table-body'),
    alertsContainer: document.getElementById('alerts-container'),
    auditContainer: document.getElementById('audit-container'),
    totalCps: document.getElementById('total-cps'),
    activeCps: document.getElementById('active-cps'),
    activeAlerts: document.getElementById('active-alerts'),
    apiCentralStatus: document.getElementById('api-central-status'),
    dbStatus: document.getElementById('db-status'),
    lastUpdate: document.getElementById('last-update'),
    filterStatus: document.getElementById('filter-status')
};

// Estado de la aplicación
const appState = {
    cps: [],
    drivers: [],
    alerts: [],
    auditLogs: [],
    filter: 'all'
};

// Utilidades
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES');
}

function updateCurrentTime() {
    const now = new Date();
    elements.currentTime.textContent = now.toLocaleTimeString('es-ES');
}

function updateLastUpdateTime() {
    elements.lastUpdate.textContent = new Date().toLocaleTimeString('es-ES');
}

// Funciones de API
async function testAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            elements.apiStatus.textContent = 'API Conectada';
            elements.apiStatus.className = 'status-indicator online';
            elements.apiCentralStatus.textContent = 'Online';
            elements.apiCentralStatus.className = 'status-badge online';
            return true;
        }
    } catch (error) {
        console.error('Error conectando a API:', error);
        elements.apiStatus.textContent = 'API Desconectada';
        elements.apiStatus.className = 'status-indicator offline';
        elements.apiCentralStatus.textContent = 'Offline';
        elements.apiCentralStatus.className = 'status-badge offline';
        return false;
    }
}

async function fetchCPs() {
    try {
        console.log('Obteniendo CPs desde:', `${API_BASE_URL}/cps`);
        const response = await fetch(`${API_BASE_URL}/cps`);
        console.log('Respuesta /cps:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const rawData = await response.json();
        console.log('Datos crudos de CPs:', rawData);
        
        if (!Array.isArray(rawData)) {
            console.error('Los datos no son un array:', rawData);
            return false;
        }
        
        // Normalizar los datos de la BD al formato esperado
        appState.cps = rawData.map(cp => ({
            id: cp.id_punto_recarga || cp.id || 'N/A',
            ubicacion: cp.ubicacion_punto_recarga || cp.ubicacion || 'N/A',
            precio: cp.precio || 0,
            estado: (cp.estado || 'DESCONECTADO').toUpperCase(),
            temperatura: cp.temperatura || 20, // Valor por defecto si no hay temperatura
            ultimaConexion: cp.ultima_conexion || cp.ultimaConexion || new Date().toISOString()
        }));
        
        console.log('CPs normalizados:', appState.cps);
        renderCPs();
        updateSystemStats();
        return true;
    } catch (error) {
        console.error('Error obteniendo CPs:', error);
        // Mostrar datos de ejemplo si la API falla (para desarrollo)
        
        renderCPs();
        updateSystemStats();
        return false;
    }
}

async function fetchDrivers() {
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios`);
        if (response.ok) {
            appState.drivers = await response.json();
            renderDrivers();
            return true;
        }
    } catch (error) {
        console.error('Error obteniendo conductores:', error);
        return false;
    }
}

async function fetchWeatherAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/weather-alerts`);
        if (response.ok) {
            appState.alerts = await response.json();
            renderAlerts();
            return true;
        }
    } catch (error) {
        console.error('Error obteniendo alertas:', error);
        return false;
    }
}

async function fetchAuditLogs() {
    try {
        const response = await fetch(`${API_BASE_URL}/audit`);
        if (response.ok) {
            appState.auditLogs = await response.json();
            renderAuditLogs();
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error obteniendo auditoría:', error);
        return false;
    }
}

async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (response.ok) {
            const stats = await response.json();
            elements.totalCps.textContent = stats.total_cps || 0;
            elements.activeCps.textContent = stats.active_cps || 0;
            elements.activeAlerts.textContent = stats.active_alerts || 0;
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error obteniendo estadísticas:', error);
        return false;
    }
}

// Renderizado
function renderCPs() {
    elements.cpsContainer.innerHTML = '';
    
    const filteredCPs = appState.filter === 'all' 
        ? appState.cps 
        : appState.cps.filter(cp => cp.estado === appState.filter);
    
    filteredCPs.forEach(cp => {
        const cpCard = document.createElement('div');
        cpCard.className = `cp-card ${cp.estado}`;
        
        // Determinar icono según estado
        let icon = 'fa-plug';
        if (cp.estado === 'SUMINISTRANDO') icon = 'fa-bolt';
        if (cp.estado === 'AVERIA') icon = 'fa-exclamation-triangle';
        if (cp.estado === 'DESCONECTADO') icon = 'fa-unlink';
        if (cp.estado === 'PARADO') icon = 'fa-pause-circle';
        
        cpCard.innerHTML = `
            <div class="cp-header">
                <div class="cp-id"><i class="fas ${icon}"></i> ${cp.id}</div>
                <span class="cp-status status-${cp.estado}">${cp.estado}</span>
            </div>
            <div class="cp-details">
                <div class="cp-detail">
                    <span class="cp-label">Ubicación:</span>
                    <span class="cp-value">${cp.ubicacion}</span>
                </div>
                <div class="cp-detail">
                    <span class="cp-label">Precio:</span>
                    <span class="cp-value">${cp.precio} €/kWh</span>
                </div>
                <div class="cp-detail">
                    <span class="cp-label">Temperatura:</span>
                    <span class="cp-value ${cp.temperatura < 0 ? 'temperature-warning' : ''}">
                        ${cp.temperatura}°C
                        ${cp.temperatura < 0 ? '<i class="fas fa-snowflake"></i>' : ''}
                    </span>
                </div>
                <div class="cp-detail">
                    <span class="cp-label">Última conexión:</span>
                    <span class="cp-value">${formatDate(cp.ultimaConexion)}</span>
                </div>
            </div>
        `;
        
        elements.cpsContainer.appendChild(cpCard);
    });
}

function renderDrivers() {
    elements.driversTableBody.innerHTML = '';
    
    appState.drivers.forEach(driver => {
        const row = document.createElement('tr');
        
        // Determinar estado del driver basado en actividad reciente
        const lastActive = new Date(driver.ultima_actividad || Date.now());
        const minutesAgo = (Date.now() - lastActive.getTime()) / (1000 * 60);
        const status = minutesAgo < 5 ? 'ACTIVO' : 'INACTIVO';
        const statusClass = status === 'ACTIVO' ? 'status-ACTIVADO' : 'status-DESCONECTADO';
        
        row.innerHTML = `
            <td>${driver.id_conductor || driver.id}</td>
            <td>${driver.nombre || 'N/A'}</td>
            <td>${driver.apellidos || 'N/A'}</td>
            <td>${driver.email_conductor || driver.correo || 'N/A'}</td>
            <td>${driver.telefono_conductor || driver.telefono || 'N/A'}</td>
            <td><span class="cp-status ${statusClass}">${status}</span></td>
        `;
        
        elements.driversTableBody.appendChild(row);
    });
}

function renderAlerts() {
    elements.alertsContainer.innerHTML = '';
    
    console.log('Alertas recibidas del API:', appState.alerts);
    
    if (appState.alerts.length === 0) {
        elements.alertsContainer.innerHTML = `
            <div class="alert-item info">
                <div class="alert-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="alert-content">
                    <h4>Sin alertas activas</h4>
                    <p>Todos los sistemas funcionando normalmente</p>
                </div>
            </div>
        `;
        return;
    }
    
    // Mostrar alertas activas
    appState.alerts.forEach(alert => {
        // Verificar que el CP asociado todavía está PARADO
        const cpIdMatch = alert.descripcion?.match(/CP (\d+)/);
        const cpId = cpIdMatch ? cpIdMatch[1] : null;
        
        const alertItem = document.createElement('div');
        alertItem.className = 'alert-item warning';
        alertItem.innerHTML = `
            <div class="alert-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="alert-content">
                <h4>⚠️ ALERTA ACTIVA</h4>
                <p>${alert.descripcion || 'Alerta meteorológica'}</p>
                <small>
                    ${formatDate(alert.fecha_hora)}
                    ${cpId ? `<br><i class="fas fa-plug"></i> CP ${cpId} - Temperatura: ${alert.cp_temperatura || alert.temperature || '?'}°C` : ''}
                </small>
            </div>
        `;
        
        elements.alertsContainer.appendChild(alertItem);
    });
}

function renderAuditLogs() {
    elements.auditContainer.innerHTML = '';
    
    appState.auditLogs.forEach(log => {
        const logItem = document.createElement('div');
        logItem.className = 'audit-item';
        
        // Determinar icono según acción
        let icon = 'fa-info-circle';
        if (log.accion.includes('weather')) icon = 'fa-cloud';
        if (log.accion.includes('auth')) icon = 'fa-key';
        if (log.accion.includes('carga')) icon = 'fa-bolt';
        
        logItem.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas ${icon}" style="color: #4fc3f7;"></i>
                <div>
                    <strong>${log.accion}</strong>
                    <p style="margin: 5px 0 0 0; color: #b0bec5;">${log.descripcion}</p>
                    <small>${formatDate(log.fecha_hora)}</small>
                </div>
            </div>
        `;
        
        elements.auditContainer.appendChild(logItem);
    });
}

function updateSystemStats() {
    const total = appState.cps.length;
    const active = appState.cps.filter(cp => cp.estado === 'ACTIVADO' || cp.estado === 'SUMINISTRANDO').length;
    const alerts = appState.alerts.filter(a => a.descripcion?.includes('ALERTA')).length;
    
    elements.totalCps.textContent = total;
    elements.activeCps.textContent = active;
    elements.activeAlerts.textContent = alerts;
}

// Funciones de actualización
async function refreshAllData() {
    console.log('Actualizando datos...');
    
    const promises = [
        testAPIConnection(),
        fetchCPs(),
        fetchDrivers(),
        fetchWeatherAlerts(),
        fetchAuditLogs(),
        fetchStats()  // ¡AÑADE ESTA LÍNEA!
    ];
    
    await Promise.all(promises);
    updateLastUpdateTime();
    console.log('Datos actualizados');
}

// Event Listeners
function setupEventListeners() {
    // Botón de actualizar CPs
    document.getElementById('refresh-cps').addEventListener('click', () => {
        fetchCPs();
        showNotification('CPs actualizados', 'success');
    });
    
    // Botón de actualizar conductores
    document.getElementById('refresh-drivers').addEventListener('click', () => {
        fetchDrivers();
        showNotification('Conductores actualizados', 'success');
    });
    
    // Botón de actualizar alertas
    document.getElementById('refresh-alerts').addEventListener('click', () => {
        fetchWeatherAlerts();
        showNotification('Alertas actualizadas', 'success');
    });

    // Botón para simular alerta
    document.getElementById('simulate-alert').addEventListener('click', () => {
        showTemperatureModal('alert');
    });
    
    // Botón para quitar alerta
    document.getElementById('remove-alert').addEventListener('click', () => {
        showTemperatureModal('remove');
    });
    
    // Filtro de estados
    elements.filterStatus.addEventListener('change', (e) => {
        appState.filter = e.target.value;
        renderCPs();
    });
    
    // Refresco automático cada 30 segundos
    refreshInterval = setInterval(refreshAllData, 30000);
}

// Funciones para simular alertas meteorológicas (como si vinieran del EV_W)
function showTemperatureModal(action) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'temp-modal';
    
    const title = action === 'alert' ? 'Simular Alerta' : 'Simular Normalización';
    const cpId = prompt("Introduce el ID del punto de carga:", "1");
    
    if (!cpId) return; // Si el usuario cancela
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3><i class="fas ${action === 'alert' ? 'fa-snowflake' : 'fa-sun'}"></i> ${title}</h3>
            <p style="color: #90a4ae; margin-bottom: 20px; text-align: center;">
                <i class="fas fa-satellite"></i> Simulando envío desde servicio meteorológico
            </p>
            <div class="temp-input-group">
                <label for="temperature">Temperatura (°C):</label>
                <input type="number" id="temperature" step="0.1" placeholder="Ej: ${action === 'alert' ? '-5' : '10'}">
                <p style="font-size: 0.8rem; color: #90a4ae; margin-top: 5px;">
                    ${action === 'alert' ? 'Debe ser menor a 0°C para activar alerta' : 'Debe ser mayor o igual a 0°C para normalizar'}
                </p>
            </div>
            <div class="modal-error" id="modal-error"></div>
            <div class="modal-buttons">
                <button id="cancel-modal" class="btn btn-secondary">Cancelar</button>
                <button id="confirm-modal" class="btn ${action === 'alert' ? 'btn-warning' : 'btn-success'}">
                    <i class="fas fa-cloud-upload-alt"></i> ${action === 'alert' ? 'Enviar Alerta' : 'Enviar Normalización'}
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    
    // Event listeners del modal
    const tempInput = modal.querySelector('#temperature');
    tempInput.focus();
    
    modal.querySelector('#cancel-modal').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.querySelector('#confirm-modal').addEventListener('click', async () => {
        const temperature = parseFloat(tempInput.value);
        const errorEl = modal.querySelector('#modal-error');
        
        // Validaciones
        if (isNaN(temperature)) {
            errorEl.textContent = 'Por favor, introduce una temperatura válida';
            errorEl.style.display = 'block';
            return;
        }
        
        if (action === 'alert' && temperature >= 0) {
            errorEl.textContent = 'Para activar alerta, la temperatura debe ser menor a 0°C';
            errorEl.style.display = 'block';
            return;
        }
        
        if (action === 'remove' && temperature < 0) {
            errorEl.textContent = 'Para normalizar, la temperatura debe ser mayor o igual a 0°C';
            errorEl.style.display = 'block';
            return;
        }
        
        // Determinar el tipo de alerta como lo haría el EV_W
        let alertType;
        
        if (action === 'alert') {
            // Si temperatura < 0, es alerta 'bajo_zero'
            alertType = 'bajo_zero';
        } else {
            // Si temperatura >= 0, es 'normal'
            alertType = 'normal';
        }
        
        // Datos que enviaría el EV_W (OpenWeather)
        const evwData = {
            cp_id: cpId,
            alert_type: alertType,
            temperature: temperature,
            source: 'simulated_weather_service', // Para identificar que es simulado
            timestamp: new Date().toISOString()
        };
        
        try {
            console.log('📡 Enviando alerta simulada desde EV_W:', evwData);
            
            const response = await fetch(`${API_BASE_URL}/weather-alert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(evwData)
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Mostrar mensaje apropiado
                if (action === 'alert') {
                    showNotification(
                        `⚠️ Alerta meteorológica simulada enviada: CP ${cpId} a ${temperature}°C`,
                        'warning'
                    );
                } else {
                    showNotification(
                        `✅ Normalización simulada enviada: CP ${cpId} a ${temperature}°C`,
                        'success'
                    );
                }
                
                console.log('Respuesta del servidor:', result);
                
                // Actualizar datos automáticamente
                setTimeout(() => {
                    refreshAllData();
                }, 1000);
                
            } else {
                const errorText = await response.text();
                throw new Error(`API respondió con error: ${response.status} - ${errorText}`);
            }
        } catch (error) {
            console.error('Error enviando alerta simulada:', error);
            showNotification(
                `❌ Error al enviar alerta simulada: ${error.message}`,
                'error'
            );
        }
        
        // Cerrar modal
        document.body.removeChild(modal);
    });
    
    // Cerrar al hacer clic fuera
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // Cerrar con ESC
    document.addEventListener('keydown', function closeModal(e) {
        if (e.key === 'Escape' && document.body.contains(modal)) {
            document.body.removeChild(modal);
            document.removeEventListener('keydown', closeModal);
        }
    });
}

// Utilidades adicionales
function showNotification(message, type = 'info') {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)';
    }
    
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Animaciones CSS para notificaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .temperature-warning {
        color: #ff9800 !important;
        font-weight: bold;
    }
`;
document.head.appendChild(style);

// Inicialización
async function init() {
    console.log('Inicializando panel de control EVCharging...');
    
    // Actualizar hora cada segundo
    setInterval(updateCurrentTime, 1000);
    updateCurrentTime();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Cargar datos iniciales
    await refreshAllData();
    
    showNotification('Panel de control cargado correctamente', 'success');
    
    console.log('Panel de control listo');
}

// Iniciar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', init);

// Manejar recarga de página
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});