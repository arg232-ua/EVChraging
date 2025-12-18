// Configuración
const API_BASE_URL = 'https://localhost:3000';
let refreshInterval = null;
let currentTab = 'dashboard';

// Elementos del DOM
const elements = {
    // Elementos generales
    currentTime: document.getElementById('current-time'),
    apiStatus: document.getElementById('api-status'),
    lastUpdate: document.getElementById('last-update'),
    
    // Elementos de dashboard
    apiCentralStatus: document.getElementById('api-central-status'),
    dbStatus: document.getElementById('db-status'),
    totalCps: document.getElementById('total-cps'),
    activeCps: document.getElementById('active-cps'),
    activeAlerts: document.getElementById('active-alerts'),
    quickCps: document.getElementById('quick-cps'),
    quickAlerts: document.getElementById('quick-alerts'),
    quickAudit: document.getElementById('quick-audit'),
    
    // Elementos de puntos de carga
    cpsContainer: document.getElementById('cps-container'),
    filterStatus: document.getElementById('filter-status'),
    
    // Elementos de conductores
    driversTableBody: document.getElementById('drivers-table-body'),
    
    // Elementos de alertas
    alertsContainer: document.getElementById('alerts-container'),
    
    // Elementos de auditoría
    auditContainer: document.getElementById('audit-container'),
    
    // Elementos del monitor meteorológico
    weatherLocationsCount: document.getElementById('weather-locations-count'),
    weatherActiveAlerts: document.getElementById('weather-active-alerts'),
    weatherLocations: document.getElementById('weather-locations'),
    weatherHistory: document.getElementById('weather-history')
};

// Estado de la aplicación
const appState = {
    cps: [],
    drivers: [],
    alerts: [],
    auditLogs: [],
    filter: 'all',
    weatherData: {
        locations: [],
        history: []
    }
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

// Funciones de navegación
function setupTabNavigation() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            
            // Actualizar pestañas activas
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Actualizar contenido activo
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
            
            currentTab = tabId;
            
            // Cargar datos específicos de la pestaña si es necesario
            loadTabSpecificData(tabId);
        });
    });
}

function loadTabSpecificData(tabId) {
    switch(tabId) {
        case 'weather':
            fetchWeatherData();
            break;
        case 'dashboard':
            updateQuickView();
            break;
        case 'charging-points':
            fetchCPs();
            break;
        case 'drivers':
            fetchDrivers();
            break;
        case 'alerts':
            fetchWeatherAlerts();
            break;
        case 'audit':
            fetchAuditLogs();
            break;
    }
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
            elements.dbStatus.textContent = 'Conectada';
            elements.dbStatus.className = 'status-badge online';
            return true;
        }
    } catch (error) {
        console.error('Error conectando a API:', error);
        elements.apiStatus.textContent = 'API Desconectada';
        elements.apiStatus.className = 'status-indicator offline';
        elements.apiCentralStatus.textContent = 'Offline';
        elements.apiCentralStatus.className = 'status-badge offline';
        elements.dbStatus.textContent = 'Desconectada';
        elements.dbStatus.className = 'status-badge offline';
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
            temperatura: cp.temperatura || 20,
            ultimaConexion: cp.ultima_conexion || cp.ultimaConexion || new Date().toISOString()
        }));
        
        console.log('CPs normalizados:', appState.cps);
        renderCPs();
        updateSystemStats();
        return true;
    } catch (error) {
        console.error('Error obteniendo CPs:', error);
        renderCPs();
        updateSystemStats();
        return false;
    }
}

async function fetchDrivers() {
    try {
        const response = await fetch(`${API_BASE_URL}/conductores-con-estado`);
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

async function fetchWeatherData() {
    try {
        // Obtener localizaciones configuradas
        const locationsResponse = await fetch(`${API_BASE_URL}/weather-locations`);
        if (locationsResponse.ok) {
            appState.weatherData.locations = await locationsResponse.json();
            renderWeatherLocations();
            elements.weatherLocationsCount.textContent = appState.weatherData.locations.length;
        } else {
            console.error('Error en /weather-locations:', locationsResponse.status);
        }
        
        // Obtener historial meteorológico (FALTA ESTE ENDPOINT)
        const historyResponse = await fetch(`${API_BASE_URL}/weather-history`);
        if (historyResponse.ok) {
            appState.weatherData.history = await historyResponse.json();
            renderWeatherHistory();
        } else {
            console.error('Error en /weather-history:', historyResponse.status);
        }
        
        // Obtener alertas activas desde la base de datos
        const alertsResponse = await fetch(`${API_BASE_URL}/weather-alerts`);
        if (alertsResponse.ok) {
            const activeAlerts = await alertsResponse.json();
            elements.weatherActiveAlerts.textContent = activeAlerts.length;
        }
        
        return true;
    } catch (error) {
        console.error('Error obteniendo datos meteorológicos:', error);
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
        
        // Usar el estado directamente de la BD
        const estado = driver.estado || 'Desconectado';
        let statusClass = 'status-DESCONECTADO';
        
        if (estado.includes('Activo')) {
            statusClass = 'status-ACTIVADO';
        } else if (estado.includes('Suministrando')) {
            statusClass = 'status-SUMINISTRANDO';
        } else if (estado.includes('Esperando')) {
            statusClass = 'status-PARADO';
        }
        
        row.innerHTML = `
            <td>${driver.id_conductor || driver.id}</td>
            <td>${driver.nombre || 'N/A'}</td>
            <td>${driver.apellidos || 'N/A'}</td>
            <td>${driver.email_conductor || driver.correo || 'N/A'}</td>
            <td>${driver.telefono_conductor || driver.telefono || 'N/A'}</td>
            <td><span class="cp-status ${statusClass}">${estado}</span></td>
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

function renderWeatherLocations() {
    elements.weatherLocations.innerHTML = '';
    
    if (appState.weatherData.locations.length === 0) {
        elements.weatherLocations.innerHTML = `
            <div class="location-card">
                <div class="location-header">
                    <span class="location-city">Sin localizaciones configuradas</span>
                </div>
                <p class="location-details">Añade localizaciones para comenzar el monitoreo meteorológico</p>
            </div>
        `;
        return;
    }
    
    appState.weatherData.locations.forEach(location => {
        // Buscar temperatura actual en el historial
        const latestEvent = appState.weatherData.history
            .filter(event => event.cp_id == location.cp_id)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];
        
        const temp = latestEvent ? latestEvent.temperature : 'N/D';
        const hasAlert = latestEvent && latestEvent.alert_type === 'bajo_zero';
        const lastUpdate = latestEvent ? formatDate(latestEvent.timestamp) : 'Nunca';
        
        const locationCard = document.createElement('div');
        locationCard.className = `location-card ${hasAlert ? 'alert' : ''}`;
        
        locationCard.innerHTML = `
            <div class="location-header">
                <span class="location-city">${location.city}, ${location.country}</span>
                <span class="location-temp ${temp < 0 ? 'warning' : ''}">
                    ${temp}°C
                    ${temp < 0 ? '<i class="fas fa-snowflake"></i>' : ''}
                </span>
            </div>
            <div class="location-details">
                <p><i class="fas fa-plug"></i> CP: ${location.cp_id}</p>
                <p><i class="fas fa-clock"></i> Última actualización: ${lastUpdate}</p>
                <p><i class="fas fa-exclamation-triangle"></i> Estado: ${hasAlert ? 'ALERTA ACTIVA' : 'Normal'}</p>
            </div>
        `;
        
        elements.weatherLocations.appendChild(locationCard);
    });
}

function renderWeatherHistory() {
    elements.weatherHistory.innerHTML = '';
    
    if (appState.weatherData.history.length === 0) {
        elements.weatherHistory.innerHTML = `
            <div class="weather-event">
                <p>No hay eventos meteorológicos registrados</p>
            </div>
        `;
        return;
    }
    
    // Ordenar por fecha más reciente
    const sortedHistory = [...appState.weatherData.history].sort((a, b) => 
        new Date(b.timestamp) - new Date(a.timestamp)
    );
    
    // Mostrar solo los últimos 20 eventos
    sortedHistory.slice(0, 20).forEach(event => {
        const eventItem = document.createElement('div');
        eventItem.className = `weather-event ${event.alert_type === 'bajo_zero' ? 'alert' : 'normal'}`;
        
        let icon = 'fa-thermometer-half';
        let status = 'Cambio de temperatura';
        
        if (event.alert_type === 'bajo_zero') {
            icon = 'fa-snowflake';
            status = 'ALERTA: Temperatura bajo cero';
        } else if (event.alert_type === 'normal') {
            icon = 'fa-sun';
            status = 'Normalización: Temperatura sobre cero';
        }
        
        eventItem.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas ${icon}"></i>
                <div style="flex: 1;">
                    <strong>${status}</strong>
                    <p style="margin: 5px 0; color: #b0bec5;">
                        CP ${event.cp_id}: ${event.temperature}°C
                        ${event.source === 'simulated_weather_service' ? ' (Simulado)' : ''}
                    </p>
                    <small>${formatDate(event.timestamp)}</small>
                </div>
            </div>
        `;
        
        elements.weatherHistory.appendChild(eventItem);
    });
}

function updateQuickView() {
    // CPs recientes (últimos 5)
    const recentCPs = [...appState.cps]
        .sort((a, b) => new Date(b.ultimaConexion) - new Date(a.ultimaConexion))
        .slice(0, 5);
    
    elements.quickCps.innerHTML = '';
    recentCPs.forEach(cp => {
        const item = document.createElement('div');
        item.className = 'quick-item';
        item.innerHTML = `
            <strong>CP ${cp.id}</strong> - ${cp.ubicacion}
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span class="cp-status status-${cp.estado}" style="font-size: 0.8rem;">${cp.estado}</span>
                <small>${formatDate(cp.ultimaConexion).split(',')[0]}</small>
            </div>
        `;
        elements.quickCps.appendChild(item);
    });
    
    // Últimas alertas (últimas 5)
    const recentAlerts = [...appState.alerts]
        .sort((a, b) => new Date(b.fecha_hora) - new Date(a.fecha_hora))
        .slice(0, 5);
    
    elements.quickAlerts.innerHTML = '';
    recentAlerts.forEach(alert => {
        const item = document.createElement('div');
        item.className = 'quick-item';
        const desc = alert.descripcion || 'Alerta meteorológica';
        item.innerHTML = `
            <strong>⚠️ ${desc.substring(0, 50)}${desc.length > 50 ? '...' : ''}</strong>
            <div style="margin-top: 5px;">
                <small>${formatDate(alert.fecha_hora)}</small>
            </div>
        `;
        elements.quickAlerts.appendChild(item);
    });
    
    // Últimos eventos de auditoría (últimos 5)
    const recentAudit = [...appState.auditLogs]
        .sort((a, b) => new Date(b.fecha_hora) - new Date(a.fecha_hora))
        .slice(0, 5);
    
    elements.quickAudit.innerHTML = '';
    recentAudit.forEach(log => {
        const item = document.createElement('div');
        item.className = 'quick-item';
        item.innerHTML = `
            <strong>${log.accion}</strong>
            <p style="margin: 5px 0; font-size: 0.9rem; color: #b0bec5;">
                ${log.descripcion.substring(0, 60)}${log.descripcion.length > 60 ? '...' : ''}
            </p>
            <small>${formatDate(log.fecha_hora)}</small>
        `;
        elements.quickAudit.appendChild(item);
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
        fetchWeatherData()
    ];
    
    await Promise.all(promises);
    updateLastUpdateTime();
    updateQuickView();
    console.log('Datos actualizados');
}

// Event Listeners
function setupEventListeners() {
    // Navegación por pestañas
    setupTabNavigation();
    
    // Botones de actualizar
    document.getElementById('refresh-cps').addEventListener('click', () => {
        fetchCPs();
        showNotification('CPs actualizados', 'success');
    });
    
    document.getElementById('refresh-drivers').addEventListener('click', () => {
        fetchDrivers();
        showNotification('Conductores actualizados', 'success');
    });
    
    document.getElementById('refresh-alerts').addEventListener('click', () => {
        fetchWeatherAlerts();
        showNotification('Alertas actualizadas', 'success');
    });
    
    document.getElementById('refresh-audit').addEventListener('click', () => {
        fetchAuditLogs();
        showNotification('Auditoría actualizada', 'success');
    });
    
    document.getElementById('refresh-weather').addEventListener('click', () => {
        fetchWeatherData();
        showNotification('Datos meteorológicos actualizados', 'success');
    });
    
    // Botones del monitor meteorológico
    document.getElementById('add-location').addEventListener('click', () => {
        showAddLocationModal();
    });
    
    document.getElementById('change-location').addEventListener('click', () => {
        showChangeLocationModal();
    });
    
    document.getElementById('simulate-alert').addEventListener('click', () => {
        showTemperatureModal('alert');
    });
    
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

// Modales
function showTemperatureModal(action) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'temp-modal';
    
    const title = action === 'alert' ? 'Simular Alerta' : 'Simular Normalización';
    const cpId = prompt("Introduce el ID del punto de carga:", "1");
    
    if (!cpId) return;
    
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
    
    const tempInput = modal.querySelector('#temperature');
    tempInput.focus();
    
    modal.querySelector('#cancel-modal').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.querySelector('#confirm-modal').addEventListener('click', async () => {
        const temperature = parseFloat(tempInput.value);
        const errorEl = modal.querySelector('#modal-error');
        
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
        
        let alertType = action === 'alert' ? 'bajo_zero' : 'normal';
        
        const evwData = {
            cp_id: cpId,
            alert_type: alertType,
            temperature: temperature,
            source: 'simulated_weather_service',
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
        
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    document.addEventListener('keydown', function closeModal(e) {
        if (e.key === 'Escape' && document.body.contains(modal)) {
            document.body.removeChild(modal);
            document.removeEventListener('keydown', closeModal);
        }
    });
}

function showAddLocationModal() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3><i class="fas fa-map-marker-alt"></i> Añadir Nueva Localización</h3>
            <p style="color: #90a4ae; margin-bottom: 20px; text-align: center;">
                Configurar nueva ciudad para monitoreo meteorológico
            </p>
            
            <div class="temp-input-group">
                <label for="cp-id">ID del Punto de Carga:</label>
                <input type="text" id="cp-id" placeholder="Ej: 1, 2, 3...">
            </div>
            
            <div class="temp-input-group">
                <label for="city">Ciudad:</label>
                <input type="text" id="city" placeholder="Ej: Madrid">
            </div>
            
            <div class="temp-input-group">
                <label for="country">País:</label>
                <select id="country">
                    <option value="ES">España</option>
                    <option value="FR">Francia</option>
                    <option value="DE">Alemania</option>
                    <option value="IT">Italia</option>
                    <option value="PT">Portugal</option>
                    <option value="UK">Reino Unido</option>
                    <option value="US">Estados Unidos</option>
                </select>
            </div>
            
            <div class="modal-error" id="modal-error"></div>
            
            <div class="modal-buttons">
                <button id="cancel-modal" class="btn btn-secondary">Cancelar</button>
                <button id="confirm-modal" class="btn btn-success">
                    <i class="fas fa-plus-circle"></i> Añadir Localización
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    
    modal.querySelector('#cp-id').focus();
    
    modal.querySelector('#cancel-modal').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.querySelector('#confirm-modal').addEventListener('click', async () => {
        const cpId = modal.querySelector('#cp-id').value.trim();
        const city = modal.querySelector('#city').value.trim();
        const country = modal.querySelector('#country').value;
        const errorEl = modal.querySelector('#modal-error');
        
        if (!cpId || !city) {
            errorEl.textContent = 'Por favor, completa todos los campos';
            errorEl.style.display = 'block';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/weather-locations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cp_id: cpId,
                    city: city,
                    country: country
                })
            });
            
            if (response.ok) {
                showNotification(
                    `✅ Localización añadida: ${city}, ${country} para CP ${cpId}`,
                    'success'
                );
                
                // Actualizar datos meteorológicos
                setTimeout(() => {
                    fetchWeatherData();
                }, 1000);
                
                document.body.removeChild(modal);
            } else {
                throw new Error('Error al añadir localización');
            }
        } catch (error) {
            errorEl.textContent = 'Error al añadir localización. Verifica la conexión con el servidor.';
            errorEl.style.display = 'block';
        }
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

function showChangeLocationModal() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3><i class="fas fa-exchange-alt"></i> Cambiar Ciudad de CP</h3>
            <p style="color: #90a4ae; margin-bottom: 20px; text-align: center;">
                Cambiar la ciudad monitoreada para un punto de carga existente
            </p>
            
            <div class="temp-input-group">
                <label for="cp-id-change">ID del Punto de Carga:</label>
                <input type="text" id="cp-id-change" placeholder="Ej: 1">
            </div>
            
            <div class="temp-input-group">
                <label for="new-city">Nueva Ciudad:</label>
                <input type="text" id="new-city" placeholder="Ej: Barcelona">
            </div>
            
            <div class="temp-input-group">
                <label for="new-country">Nuevo País:</label>
                <select id="new-country">
                    <option value="ES">España</option>
                    <option value="FR">Francia</option>
                    <option value="DE">Alemania</option>
                    <option value="IT">Italia</option>
                    <option value="PT">Portugal</option>
                    <option value="UK">Reino Unido</option>
                    <option value="US">Estados Unidos</option>
                </select>
            </div>
            
            <div class="modal-error" id="modal-error"></div>
            
            <div class="modal-buttons">
                <button id="cancel-modal" class="btn btn-secondary">Cancelar</button>
                <button id="confirm-modal" class="btn btn-warning">
                    <i class="fas fa-exchange-alt"></i> Cambiar Ciudad
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    
    modal.querySelector('#cp-id-change').focus();
    
    modal.querySelector('#cancel-modal').addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    document.querySelector('#confirm-modal').addEventListener('click', async () => {
        const cpId = modal.querySelector('#cp-id-change').value.trim();
        const newCity = modal.querySelector('#new-city').value.trim();
        const newCountry = modal.querySelector('#new-country').value;
        const errorEl = modal.querySelector('#modal-error');
        
        if (!cpId || !newCity) {
            errorEl.textContent = 'Por favor, completa todos los campos';
            errorEl.style.display = 'block';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/weather-locations/${cpId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    city: newCity,
                    country: newCountry,
                    force_refresh: true  // Bandera para forzar actualización
                })
            });
            
            if (response.ok) {
                showNotification(
                    `✅ Ciudad cambiada para CP ${cpId}: ${newCity}, ${newCountry}`,
                    'success'
                );
                
                // FORZAR una actualización inmediata de datos meteorológicos
                setTimeout(() => {
                    fetchWeatherData();
                    
                    // También notificar a EV_W que cambió la ciudad
                    notifyWeatherService(cpId, newCity, newCountry);
                }, 500);
                
                document.body.removeChild(modal);
            } else {
                throw new Error('Error al cambiar ciudad');
            }
        } catch (error) {
            errorEl.textContent = 'Error al cambiar ciudad. Verifica que el CP exista.';
            errorEl.style.display = 'block';
        }
    });

    // Función auxiliar para notificar a EV_W

    async function notifyWeatherService(cpId, city, country) {
        try {
            console.log(`🔄 Forzando actualización en EV_W para CP ${cpId} -> ${city}, ${country}`);
            
            // Forzar una nueva verificación de temperaturas después de 2 segundos
            setTimeout(() => {
                console.log(`Forzando actualización de temperaturas para CP ${cpId}`);
                fetchWeatherData();
            }, 2000);
            
        } catch (error) {
            console.error('Error notificando a EV_W:', error);
        }
    }
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// Utilidades adicionales
function showNotification(message, type = 'info') {
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
    } else if (type === 'warning') {
        notification.style.background = 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)';
    }
    
    document.body.appendChild(notification);
    
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