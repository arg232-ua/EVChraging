const express = require("express"); 
const centralSD = express(); 
const path = require('path');
const mysql = require("mysql"); 
const bodyParser = require("body-parser"); 

const https = require('https');
const fs = require('fs');


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
    
    const sql = `SELECT a.*, pr.estado as cp_estado, pr.temperatura as cp_temperatura FROM auditoria a LEFT JOIN punto_recarga pr ON a.descripcion LIKE CONCAT('%CP ', pr.id_punto_recarga, '%')
        WHERE a.accion = 'weather_alert' AND a.descripcion LIKE '%ALERTA METEOROLÓGICA%' AND pr.estado = 'PARADO' AND pr.temperatura < 0
        AND a.fecha_hora = (
            SELECT MAX(fecha_hora) 
            FROM auditoria a2 
            WHERE a2.accion = 'weather_alert' 
            AND a2.descripcion LIKE CONCAT('%CP ', pr.id_punto_recarga, '%')
            AND a2.descripcion LIKE '%ALERTA METEOROLÓGICA%'
        )
        ORDER BY a.fecha_hora DESC`;
    connection.query(sql, (error, results) => {
        if (error) {
            console.error('❌ Error en /weather-alerts:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos',
                details: error.message 
            });
        }
        console.log(`✅ Alertas meteorológicas activas obtenidas: ${results.length} registros`);
        response.json(results);
    });
});

// Endpoint para RECIBIR alertas meteorológicas del EV_W
// Endpoint para RECIBIR alertas meteorológicas del EV_W
centralSD.post("/weather-alert", (request, response) => {
    console.log('Solicitud POST /weather-alert recibida:', request.body);
    
    const { cp_id, alert_type, temperature } = request.body;
    
    if (!cp_id || !alert_type || temperature === undefined) {
        return response.status(400).json({ 
            error: 'Datos incompletos',
            required: ['cp_id', 'alert_type', 'temperature'] 
        });
    }
    
    // Verificar el estado ACTUAL del CP
    const checkCPSql = `SELECT estado, temperatura FROM punto_recarga WHERE id_punto_recarga = ?`;
    
    connection.query(checkCPSql, [cp_id], (checkErr, checkResult) => {
        if (checkErr) {
            console.error('Error consultando CP:', checkErr.message);
            return response.status(500).json({ error: 'Error consultando CP' });
        }
        
        if (checkResult.length === 0) {
            return response.status(404).json({ error: `CP ${cp_id} no encontrado` });
        }
        
        const cpEstadoActual = checkResult[0].estado;
        const cpTemperaturaActual = checkResult[0].temperatura;
        
        // Determinar si este es un cambio REAL o no
        let esAlertaNueva = false;
        let esNormalizacion = false;
        
        if (alert_type === 'bajo_zero' && temperature < 0 && cpEstadoActual !== 'PARADO') {
            esAlertaNueva = true;
        } else if (alert_type === 'normal' && temperature >= 0 && cpEstadoActual === 'PARADO') {
            esNormalizacion = true;
        }
        
        // Insertar en auditoría SOLO si hay cambio real
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
            nuevoEstado = null;
        } else {
            descripcion = `Informe meteorológico: Temperatura ${temperature}°C en CP ${cp_id}`;
            nuevoEstado = null;
        }
        
        // Solo insertar en auditoría si hay cambio o es importante
        if (esAlertaNueva || esNormalizacion || alert_type === 'cambio_temperatura') {
            const auditSql = `INSERT INTO auditoria (fecha_hora, ip_origen, accion, descripcion) VALUES (NOW(), 'EV_W', 'weather_alert', ?)`;
            
            connection.query(auditSql, [descripcion], (err1) => {
                if (err1) console.error('Error en auditoría:', err1.message);
                procesarActualizacion();
            });
        } else {
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
            console.log(`Alerta procesada: CP ${cp_id} - ${temperature}°C - ${alert_type}`);
            response.json({ 
                success: true, 
                message: `Temperatura actualizada para CP ${cp_id}`,
                temperature: temperature,
                state_changed: (esAlertaNueva || esNormalizacion),
                is_new_alert: esAlertaNueva,
                is_normalization: esNormalizacion
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