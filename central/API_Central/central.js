const express = require("express"); 
const centralSD = express(); 
const path = require('path');
const mysql = require("mysql"); 
const bodyParser = require("body-parser"); 

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
centralSD.use(express.static(__dirname));

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
    const sql = 'SELECT id_punto_recarga, ubicacion_punto_recarga, precio, estado FROM punto_recarga';
    
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
        active_alerts: "SELECT COUNT(*) as count FROM auditoria WHERE accion = 'weather_alert' AND fecha_hora > DATE_SUB(NOW(), INTERVAL 1 HOUR)"
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
    
    const sql = "SELECT * FROM auditoria WHERE accion = 'weather_alert' ORDER BY fecha_hora DESC LIMIT 10";
    connection.query(sql, (error, results) => {
        if (error) {
            console.error('❌ Error en /weather-alerts:', error.message);
            return response.status(500).json({ 
                error: 'Error en la base de datos',
                details: error.message 
            });
        }
        console.log(`✅ Alertas meteorológicas obtenidas: ${results.length} registros`);
        response.json(results);
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
centralSD.listen(port, () => { 
    console.log(`🚀 API REST de la central ejecutándose en: http://localhost:${port}`);
    console.log(`📊 Endpoints disponibles:`);
    console.log(`   http://localhost:${port}/cps`);
    console.log(`   http://localhost:${port}/audit`);
    console.log(`   http://localhost:${port}/stats`);
    console.log(`   http://localhost:${port}/usuarios`);
    console.log(`   http://localhost:${port}/weather-alerts`);
});