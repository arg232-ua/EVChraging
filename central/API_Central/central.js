const express = require("express"); 
const centralSD = express(); 
const path = require('path');
const mysql = require("mysql"); 
const bodyParser = require("body-parser"); 

// Ruta al archivo de configuración de EV_W
const WEATHER_CONFIG_PATH = path.join(__dirname, '..', '..', 'EV_W', 'weather_config.json');

const https = require('https');
const fs = require('fs');
const fsPromises = fs.promises;


const sslOptions = {
    key: fs.readFileSync(path.join(__dirname, '..', '..', 'cp', 'API_Registry', 'key.pem')),
    cert: fs.readFileSync(path.join(__dirname, '..', '..', 'cp', 'API_Registry', 'cert.pem'))
};

// Se define el puerto 
const port = 3000;

// CORS
centralSD.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
    }
    next();
});

// Body parser para JSON
centralSD.use(bodyParser.json());
centralSD.use(bodyParser.urlencoded({ extended: true }));
centralSD.use(express.static(path.join(__dirname, 'public')));

// Configuración de la conexión a la base de datos MySQL 
const connection = mysql.createConnection({ 
    host: 'localhost', 
    user: 'sd_remoto', 
    password: '1234', 
    database: 'evcharging' 
}); 

// Comprobar conexión a la base de datos 
connection.connect(error => { 
    if (error) {
        console.error('❌ Error conectando a la base de datos:', error.message);
        process.exit(1);
    }
    console.log('✅ Conexión a la base de datos evcharging correcta'); 
}); 

centralSD.get("/", (req, res) => { 
    res.json({
        message: 'API CENTRAL de SD funcionando',
        version: '1.0.0',
        endpoints: ['/usuarios', '/cps', '/audit', '/stats', '/weather-alerts']
    });
}); 

centralSD.get("/test", (req, res) => {
    res.json({
        status: 'ok', 
        message: 'API funcionando correctamente',
        timestamp: new Date().toISOString()
    });
});

// Obtener todos los puntos de carga
centralSD.get("/cps", (request, response) => {
    console.log('📡 Solicitud GET /cps recibida');
    const sql = 'SELECT id_punto_recarga, ubicacion_punto_recarga, precio, estado, temperatura, activo, credencial, tiene_clave_simetrica FROM punto_recarga';
    
    connection.query(sql, (error, resultado) => {
        if (error) {
            console.error('❌ Error en /cps:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos', 
                details: error.message 
            });
        }
        console.log(`✅ CPs obtenidos: ${resultado.length} registros`);
        response.json(resultado);
    });
});

// Obtener auditoría
centralSD.get("/audit", (request, response) => {
    console.log('📡 Solicitud GET /audit recibida');
    const sql = "SELECT * FROM auditoria ORDER BY fecha_hora DESC LIMIT 20";
    
    connection.query(sql, (error, resultado) => {
        if (error) {
            console.error('❌ Error en /audit:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos', 
                details: error.message 
            });
        }
        console.log(`✅ Eventos de auditoría obtenidos: ${resultado.length} registros`);
        response.json(resultado);
    });
});

// Obtener estadísticas del sistema
centralSD.get("/stats", (request, response) => {
    console.log('📡 Solicitud GET /stats recibida');
    
    const queries = {
        total_cps: 'SELECT COUNT(*) as count FROM punto_recarga',
        active_cps: "SELECT COUNT(*) as count FROM punto_recarga WHERE estado IN ('ACTIVADO', 'SUMINISTRANDO')",
        total_drivers: 'SELECT COUNT(*) as count FROM conductor',
        active_alerts: "SELECT COUNT(DISTINCT pr.id_punto_recarga) as count FROM punto_recarga pr WHERE pr.estado = 'PARADO' AND pr.temperatura < 0"
    };

    Promise.all(Object.values(queries).map(query => 
        new Promise((resolve, reject) => {
            connection.query(query, (error, result) => {
                if (error) reject(error);
                else resolve(result[0].count);
            });
        })
    )).then(results => {
        const stats = {
            total_cps: results[0] || 0,
            active_cps: results[1] || 0,
            total_drivers: results[2] || 0,
            active_alerts: results[3] || 0
        };
        console.log(`✅ Estadísticas obtenidas:`, stats);
        response.json(stats);
    }).catch(error => {
        console.error('❌ Error en /stats:', error.message);
        response.status(500).json({ 
            error: 'Error obteniendo estadísticas', 
            details: error.message 
        });
    });
});

// Endpoint para consultar alertas meteorológicas
centralSD.get("/weather-alerts", (request, response) => {
    console.log('📡 Solicitud GET /weather-alerts recibida');
    
    const sql = `SELECT a.* FROM auditoria a
        WHERE a.accion = 'weather_alert' 
        AND a.descripcion LIKE '%ALERTA METEOROLÓGICA%'
        AND a.alerta_activa = TRUE
        ORDER BY a.fecha_hora DESC`;
    
    connection.query(sql, (error, results) => {
        if (error) {
            console.error('❌ Error en /weather-alerts:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos',
                details: error.message 
            });
        }
        console.log(`Alertas meteorológicas activas: ${results.length} registros`);
        response.json(results);
    });
});

// Obtener alertas meteorológicas ACTIVAS (temperatura < 0)
centralSD.get("/weather-active-alerts", (request, response) => {
    console.log('📡 Solicitud GET /weather-active-alerts recibida');
    
    const sql = `SELECT pr.id_punto_recarga, pr.temperatura, a.descripcion, a.fecha_hora 
                 FROM punto_recarga pr
                 LEFT JOIN auditoria a ON a.descripcion LIKE CONCAT('%CP ', pr.id_punto_recarga, '%')
                 WHERE pr.temperatura < 0 
                 AND pr.estado = 'PARADO'
                 AND a.accion = 'weather_alert'
                 AND a.descripcion LIKE '%ALERTA METEOROLÓGICA%'
                 AND a.fecha_hora = (
                     SELECT MAX(fecha_hora) 
                     FROM auditoria a2 
                     WHERE a2.accion = 'weather_alert' 
                     AND a2.descripcion LIKE CONCAT('%CP ', pr.id_punto_recarga, '%')
                 )`;
    
    connection.query(sql, (error, results) => {
        if (error) {
            console.error('❌ Error en /weather-active-alerts:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos',
                details: error.message 
            });
        }
        console.log(`✅ Alertas activas obtenidas: ${results.length} registros`);
        response.json(results);
    });
});

// Endpoint para RECIBIR alertas meteorológicas del EV_W
centralSD.post("/weather-alert", (request, response) => {
    console.log('Solicitud POST /weather-alert recibida:', request.body);
    
    const { cp_id, alert_type, temperature } = request.body;
    
    if (!cp_id || !alert_type || temperature === undefined || temperature === null) {
        console.error('Datos incompletos o inválidos:', { cp_id, alert_type, temperature });
        return response.status(400).json({ 
            error: 'Datos incompletos',
            received: request.body
        });
    }
    
    console.log(`Procesando: CP ${cp_id}, Temp: ${temperature}°C, Tipo: ${alert_type}`);
    
    // Verificar el estado ACTUAL del CP
    const checkCPSql = `SELECT estado, temperatura FROM punto_recarga WHERE id_punto_recarga = ?`;
    
    connection.query(checkCPSql, [cp_id], (checkErr, checkResult) => {
        if (checkErr) {
            console.error('Error consultando CP:', checkErr.message);
            return response.status(500).json({ error: 'Error consultando CP' });
        }
        
        if (checkResult.length === 0) {
            console.error(`CP ${cp_id} no encontrado`);
            return response.status(404).json({ error: `CP ${cp_id} no encontrado` });
        }
        
        const cpEstadoActual = checkResult[0].estado;
        const cpTemperaturaActual = checkResult[0].temperatura;
        
        console.log(`Estado actual CP ${cp_id}: ${cpEstadoActual}, Temp: ${cpTemperaturaActual}°C`);
        
        // Determinar si este es un cambio REAL o no
        let esAlertaNueva = false;
        let esNormalizacion = false;
        let alertaActiva = false;  // Nuevo: estado de la alerta
        
        if (alert_type === 'bajo_zero' && temperature < 0 && cpEstadoActual !== 'PARADO') {
            esAlertaNueva = true;
            alertaActiva = true;  // Nueva alerta → activa
            console.log(`NUEVA ALERTA: CP ${cp_id} bajo cero`);
        } else if (alert_type === 'normal' && temperature >= 0 && cpEstadoActual === 'PARADO') {
            esNormalizacion = true;
            alertaActiva = false; // Normalización → desactivar
            console.log(`NORMALIZACIÓN: CP ${cp_id} vuelve a temperatura normal`);
        } else if (alert_type === 'bajo_zero' && temperature < 0) {
            // Temperatura sigue bajo cero, mantener alerta activa
            alertaActiva = true;
            console.log(`ALERTA ACTIVA: CP ${cp_id} sigue bajo cero`);
        } else if (alert_type === 'normal' && temperature >= 0) {
            // Temperatura normal, sin alerta activa
            alertaActiva = false;
            console.log(`TEMPERATURA NORMAL: CP ${cp_id}`);
        }
        
        // Construir descripción según el tipo de alerta
        let descripcion;
        let nuevoEstado;
        
        if (alert_type === 'bajo_zero') {
            descripcion = `ALERTA METEOROLÓGICA: Temperatura ${temperature}°C en CP ${cp_id}`;
            nuevoEstado = 'PARADO';
        } else if (alert_type === 'normal') {
            descripcion = `NORMALIZACIÓN: Temperatura ${temperature}°C en CP ${cp_id}`;
            nuevoEstado = 'ACTIVADO';
        } else if (alert_type === 'cambio_temperatura') {
            descripcion = `ACTUALIZACIÓN: Nueva temperatura ${temperature}°C en CP ${cp_id}`;
            nuevoEstado = null;  // No cambiar estado, solo temperatura
        } else if (alert_type === 'cambio_ciudad') {
            descripcion = `CAMBIO DE CIUDAD: CP ${cp_id} ahora monitorea nueva ubicación. Temperatura: ${temperature}°C`;
            nuevoEstado = null;  // No cambiar estado, solo temperatura
        } else {
            descripcion = `Informe meteorológico: Temperatura ${temperature}°C en CP ${cp_id}`;
            nuevoEstado = null;
        }
        
        console.log(`Descripción: ${descripcion}`);
        console.log(`Estado nuevo: ${nuevoEstado || 'sin cambio'}, Alerta activa: ${alertaActiva}`);
        
        // Solo insertar en auditoría si hay cambio o es importante
        if (esAlertaNueva || esNormalizacion || alert_type === 'cambio_temperatura') {
            // IMPORTANTE: Ahora usamos alerta_activa
            const auditSql = `INSERT INTO auditoria (fecha_hora, ip_origen, accion, descripcion, alerta_activa) 
                             VALUES (NOW(), 'EV_W', 'weather_alert', ?, ?)`;
            
            console.log(`Insertando en auditoría con alerta_activa = ${alertaActiva}`);
            
            connection.query(auditSql, [descripcion, alertaActiva], (err1) => {
                if (err1) {
                    console.error('Error en auditoría:', err1.message);
                    // Continuar aunque falle la auditoría
                } else {
                    console.log(`Registro de auditoría creado (ID: ${err1?.insertId || 'N/A'})`);
                }
                procesarActualizacion();
            });
        } else {
            console.log(`No se requiere auditoría para este evento`);
            procesarActualizacion();
        }
        
        function procesarActualizacion() {
            // Actualizar temperatura SIEMPRE
            const updateTempSql = `UPDATE punto_recarga SET temperatura = ? WHERE id_punto_recarga = ?`;
            
            connection.query(updateTempSql, [temperature, cp_id], (err2) => {
                if (err2) {
                    console.error('Error actualizando temperatura:', err2.message);
                } else {
                    console.log(`Temperatura actualizada: CP ${cp_id} = ${temperature}°C`);
                }
                
                // Actualizar estado solo si es necesario
                if (nuevoEstado !== null && (esAlertaNueva || esNormalizacion)) {
                    const updateEstadoSql = `UPDATE punto_recarga SET estado = ? WHERE id_punto_recarga = ?`;
                    
                    connection.query(updateEstadoSql, [nuevoEstado, cp_id], (err3) => {
                        if (err3) {
                            console.error('Error actualizando estado:', err3.message);
                        } else {
                            console.log(`Estado actualizado: CP ${cp_id} = ${nuevoEstado}`);
                        }
                        
                        finalizarRespuesta();
                    });
                } else {
                    finalizarRespuesta();
                }
            });
        }
        
        function finalizarRespuesta() {
            console.log(`Alerta procesada exitosamente: CP ${cp_id} - ${temperature}°C - ${alert_type}`);
            
            // También actualizar otras alertas del mismo CP para mantener consistencia
            if (esNormalizacion && alertaActiva === false) {
                // Si es una normalización, desactivar cualquier alerta previa del mismo CP que esté activa
                const sqlDesactivarPrevias = `
                    UPDATE auditoria 
                    SET alerta_activa = FALSE 
                    WHERE accion = 'weather_alert' 
                    AND descripcion LIKE CONCAT('%CP ', ?, '%')
                    AND alerta_activa = TRUE
                    AND id_auditoria != LAST_INSERT_ID()
                `;
                
                connection.query(sqlDesactivarPrevias, [cp_id], (err4) => {
                    if (err4) {
                        console.error('Error desactivando alertas previas:', err4.message);
                    } else if (err4?.affectedRows > 0) {
                        console.log(`🔄 ${err4.affectedRows} alertas previas desactivadas para CP ${cp_id}`);
                    }
                });
            }
            
            response.json({ 
                success: true, 
                message: `Temperatura actualizada para CP ${cp_id}`,
                temperature: temperature,
                state_changed: (esAlertaNueva || esNormalizacion),
                is_new_alert: esAlertaNueva,
                is_normalization: esNormalizacion,
                alert_active: alertaActiva,
                timestamp: new Date().toISOString()
            });
        }
    });
});

// Listado de todos los usuarios (conductores)
centralSD.get("/usuarios", (request, response) => { 
    console.log('📡 Solicitud GET /usuarios recibida');
    
    const sql = 'SELECT * FROM conductor'; 
    connection.query(sql, (error, resultado) => { 
        if (error) {
            console.error('❌ Error en /usuarios:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos',
                details: error.message 
            });
        }
        console.log(`✅ Conductores obtenidos: ${resultado.length} registros`);
        response.json(resultado); 
    }); 
});

// Obtener todos los conductores con su estado
centralSD.get("/conductores-con-estado", (request, response) => {
    console.log('📡 Solicitud GET /conductores-con-estado recibida');
    
    const sql = 'SELECT id_conductor, nombre, apellidos, email_conductor, telefono_conductor, estado FROM conductor ORDER BY id_conductor';
    
    connection.query(sql, (error, resultado) => {
        if (error) {
            console.error('❌ Error en /conductores-con-estado:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos', 
                details: error.message 
            });
        }
        console.log(`✅ Conductores con estado obtenidos: ${resultado.length} registros`);
        response.json(resultado);
    });
});

// ==============================================
// ENDPOINTS PARA EL FRONTEND DE METEOROLOGÍA
// ==============================================

// 1. Obtener localizaciones configuradas
centralSD.get("/weather-locations", async (request, response) => {
    console.log('📡 Solicitud GET /weather-locations recibida');
    
    try {
        // Usar fsPromises.readFile en lugar de fs.readFile
        const data = await fsPromises.readFile(WEATHER_CONFIG_PATH, 'utf8');
        const config = JSON.parse(data);
        console.log(`✅ Localizaciones obtenidas: ${config.locations?.length || 0}`);
        response.json(config.locations || []);
    } catch (error) {
        console.error('❌ Error leyendo weather_config.json:', error.message);
        response.status(500).json({ 
            error: 'Error leyendo configuración meteorológica',
            details: error.message 
        });
    }
});

// 3. Añadir nueva localización (para que el frontend pueda modificar)
centralSD.post("/weather-locations", async (request, response) => {
    console.log('📡 Solicitud POST /weather-locations recibida:', request.body);
    
    const { cp_id, city, country } = request.body;
    
    if (!cp_id || !city || !country) {
        return response.status(400).json({ 
            error: 'Datos incompletos',
            required: ['cp_id', 'city', 'country'] 
        });
    }
    
    try {
        // Leer configuración actual - usar fsPromises
        const data = await fsPromises.readFile(WEATHER_CONFIG_PATH, 'utf8');
        const config = JSON.parse(data);
        
        // Verificar si el CP ya existe
        const existingIndex = config.locations.findIndex(loc => loc.cp_id === cp_id);
        
        if (existingIndex !== -1) {
            // Actualizar localización existente
            config.locations[existingIndex] = { cp_id, city, country };
        } else {
            // Añadir nueva localización
            config.locations.push({ cp_id, city, country });
        }
        
        // Guardar archivo - usar fsPromises
        await fsPromises.writeFile(WEATHER_CONFIG_PATH, JSON.stringify(config, null, 2));
        
        console.log(`✅ Localización guardada en weather_config.json: CP ${cp_id} - ${city}, ${country}`);
        
        // Registrar en auditoría
        const auditSql = `INSERT INTO auditoria (fecha_hora, ip_origen, accion, descripcion) 
                         VALUES (NOW(), 'Frontend', 'config_update', ?)`;
        const descripcion = `Configuración meteorológica actualizada: CP ${cp_id} - ${city}, ${country}`;
        
        connection.query(auditSql, [descripcion], (auditError) => {
            if (auditError) console.error('Error en auditoría:', auditError.message);
        });
        
        response.json({ 
            success: true, 
            message: 'Localización guardada correctamente',
            location: { cp_id, city, country }
        });
        
    } catch (error) {
        console.error('❌ Error guardando localización:', error.message);
        response.status(500).json({ 
            error: 'Error guardando localización',
            details: error.message 
        });
    }
});

// 4. Actualizar localización existente
centralSD.put("/weather-locations/:cp_id", async (request, response) => {
    const { cp_id } = request.params;
    const { city, country } = request.body;
    
    console.log(`📡 Solicitud PUT /weather-locations/${cp_id}:`, { city, country });
    
    if (!city || !country) {
        return response.status(400).json({ 
            error: 'Datos incompletos',
            required: ['city', 'country'] 
        });
    }
    
    try {
        // Leer configuración actual - usar fsPromises
        const data = await fsPromises.readFile(WEATHER_CONFIG_PATH, 'utf8');
        const config = JSON.parse(data);
        
        const locationIndex = config.locations.findIndex(loc => loc.cp_id === cp_id);
        
        if (locationIndex === -1) {
            return response.status(404).json({ 
                error: 'Localización no encontrada',
                message: `No se encontró el CP ${cp_id} en la configuración`
            });
        }
        
        // Guardar datos antiguos para el log
        const oldLocation = { ...config.locations[locationIndex] };
        
        // Actualizar localización
        config.locations[locationIndex] = {
            ...config.locations[locationIndex],
            city,
            country
        };
        
        // Guardar archivo - usar fsPromises
        await fsPromises.writeFile(WEATHER_CONFIG_PATH, JSON.stringify(config, null, 2));
        
        console.log(`✅ Localización actualizada: CP ${cp_id} - ${city}, ${country}`);
        
        // Registrar en auditoría
        const auditSql = `INSERT INTO auditoria (fecha_hora, ip_origen, accion, descripcion) 
                         VALUES (NOW(), 'Frontend', 'config_update', ?)`;
        const descripcion = `Ciudad cambiada para CP ${cp_id}: ${oldLocation.city},${oldLocation.country} → ${city},${country}`;
        
        connection.query(auditSql, [descripcion], (auditError) => {
            if (auditError) console.error('Error en auditoría:', auditError.message);
        });
        
        response.json({ 
            success: true, 
            message: 'Localización actualizada correctamente',
            old_location: oldLocation,
            new_location: config.locations[locationIndex]
        });
        
    } catch (error) {
        console.error('❌ Error actualizando localización:', error.message);
        response.status(500).json({ 
            error: 'Error actualizando localización',
            details: error.message 
        });
    }
});

// Añade este endpoint al archivo centralSD.js:
centralSD.get("/weather-history", (request, response) => {
    console.log('📡 Solicitud GET /weather-history recibida');
    
    const sql = `SELECT * FROM auditoria 
                 WHERE accion = 'weather_alert' 
                 ORDER BY fecha_hora DESC 
                 LIMIT 50`;
    
    connection.query(sql, (error, results) => {
        if (error) {
            console.error('❌ Error en /weather-history:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos',
                details: error.message 
            });
        }
        
        // Transformar resultados para el frontend
        const history = results.map(row => ({
            cp_id: extractCPIdFromDescription(row.descripcion),
            alert_type: getAlertTypeFromDescription(row.descripcion),
            temperature: extractTemperatureFromDescription(row.descripcion),
            timestamp: row.fecha_hora,
            source: 'database'
        }));
        
        console.log(`✅ Historial meteorológico obtenido: ${history.length} registros`);
        response.json(history);
    });
});

// Funciones auxiliares
function extractCPIdFromDescription(desc) {
    const match = desc.match(/CP (\d+)/);
    return match ? match[1] : null;
}

function getAlertTypeFromDescription(desc) {
    if (desc.includes('ALERTA METEOROLÓGICA')) return 'bajo_zero';
    if (desc.includes('NORMALIZACIÓN')) return 'normal';
    if (desc.includes('ACTUALIZACIÓN')) return 'cambio_temperatura';
    return 'unknown';
}

function extractTemperatureFromDescription(desc) {
    const match = desc.match(/(?:Temperatura|temperatura) (-?\d+(?:\.\d+)?)/);
    return match ? parseFloat(match[1]) : null;
}

centralSD.use((req, res, next) => {
    const error = new Error('Ruta no encontrada');
    error.status = 404;
    next(error);
});

centralSD.use((error, req, res, next) => {
    res.status(error.status || 500);
    res.json({
        error: {
            message: error.message,
            path: req.originalUrl
        }
    });
});

// Ejecutar la aplicación
https.createServer(sslOptions, centralSD).listen(port, () => { 
    console.log(`🚀 API REST de la central ejecutándose en: https://localhost:${port}`);
    console.log(`📊 Endpoints disponibles:`);
    console.log(`   https://localhost:${port}/cps`);
    console.log(`   https://localhost:${port}/audit`);
    console.log(`   https://localhost:${port}/stats`);
    console.log(`   https://localhost:${port}/usuarios`);
    console.log(`   https://localhost:${port}/weather-alerts`);
    console.log(`🌐 Panel web disponible en: https://localhost:${port}/`);
});