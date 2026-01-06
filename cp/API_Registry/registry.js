const express = require("express");
const registry = express();
const port = 3001;
const mysql = require("mysql");
const bodyParser = require("body-parser");
const { generarCredencial } = require("./utils");
const https = require("https");
const fs = require("fs");
const options = {
    key: fs.readFileSync("key.pem"),
    cert: fs.readFileSync("cert.pem")
};

// Middleware
registry.use(bodyParser.json());

// Conexión MySQL
const connection = mysql.createConnection({
    host: '127.0.0.1',
    user: 'sd_remoto',
    password: '1234',
    database: 'evcharging'
});


connection.connect(error => {
    if (error) throw error;
    console.log("Conexión a la base de datos evcharging correcta");
});



// REGISTRAR CP (POST)

registry.post("/registro", (req, res) => {
    const { cp_logico, id_central, ubicacion_punto_recarga, precio, estado } = req.body;

    if (!cp_logico || !id_central || !ubicacion_punto_recarga) {
    return res.status(400).json({ error: "Faltan datos obligatorios" });
}

    const sqlBuscar = `
    SELECT id_punto_recarga
    FROM punto_recarga
    WHERE cp_logico = ?
    `;

    connection.query(sqlBuscar, [cp_logico], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });

        const credencial = generarCredencial();

        if (rows.length > 0) {
            // CP EXISTENTE → solo actualizar credencial
            const id_cp_bd = rows[0].id_punto_recarga;

            const sqlUpdate = `
            UPDATE punto_recarga
            SET credencial = ?, activo = 1
            WHERE id_punto_recarga = ?
            `;

            connection.query(sqlUpdate, [credencial, id_cp_bd], err2 => {
                if (err2) return res.status(500).json({ error: err2.message });

                return res.json({
                    message: "CP existente. Credencial actualizada",
                    id_punto_recarga: id_cp_bd,
                    credencial
                });
            });

        } else {
            // CP NUEVO → crear
            const sqlInsert = `
            INSERT INTO punto_recarga
            (cp_logico, id_central, ubicacion_punto_recarga, precio, estado, credencial, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            `;

            connection.query(
                sqlInsert,
                [cp_logico, id_central, ubicacion_punto_recarga, precio, estado, credencial],
                (err3, result) => {
                    if (err3) return res.status(500).json({ error: err3.message });

                    return res.json({
                        message: "CP nuevo creado",
                        id_punto_recarga: result.insertId,
                        credencial
                    });
                }
            );
        }
    });
});



// DAR DE BAJA CP (DELETE)

registry.delete("/registro/:id", (req, res) => {
    const id = req.params.id;

    const sql = "UPDATE punto_recarga SET activo = 0 WHERE id_punto_recarga = ?";

    connection.query(sql, [id], (error, result) => {
        if (error) return res.status(500).json({ error: error.message });

        if (result.affectedRows === 0) {
            return res.status(404).json({ error: "CP no encontrado" });
        }

        res.json({ message: "CP dado de baja correctamente" });
    });
});


//REACTIVAR CP (PUT)

registry.put("/registro/reactivar/:id", (req, res) => {
    const id = req.params.id;

    // 1. Ver si existe el CP
    const sqlSelect = "SELECT * FROM punto_recarga WHERE id_punto_recarga = ?";

    connection.query(sqlSelect, [id], (error, rows) => {
        if (error) return res.status(500).json({ error: error.message });

        if (rows.length === 0) {
            return res.status(404).json({ error: "CP no encontrado" });
        }

        const cp = rows[0];

        // 2. Si ya está activo, no hace falta reactivarlo
        if (cp.activo === 1) {
            return res.status(400).json({ error: "El CP ya está dado de alta" });
        }

        // 3. Generar nueva credencial
        const nuevaCredencial = generarCredencial();

        // 4. Reactivar el CP
        const sqlUpdate = `
            UPDATE punto_recarga 
            SET activo = 1, credencial = ?
            WHERE id_punto_recarga = ?
        `;

        connection.query(sqlUpdate, [nuevaCredencial, id], (err2, result) => {
            if (err2) return res.status(500).json({ error: err2.message });

            res.json({
                message: "CP reactivado correctamente",
                id_punto_recarga: id,
                nueva_credencial: nuevaCredencial
            });
        });
    });
});


// CONSULTAR CP POR ID (GET)

registry.get("/registro/:id", (req, res) => {
    const id = req.params.id;

    const sql = "SELECT * FROM punto_recarga WHERE id_punto_recarga = ?";

    connection.query(sql, [id], (error, rows) => {
        if (error) return res.status(500).json({ error: error.message });

        if (rows.length === 0) {
            return res.status(404).json({ error: "CP no encontrado" });
        }

        res.json(rows[0]);
    });
});



//LISTAR TODOS LOS CPs (GET)

registry.get("/registro", (req, res) => {
    const sql = "SELECT * FROM punto_recarga";

    connection.query(sql, (error, rows) => {
        if (error) return res.status(500).json({ error: error.message });

        res.json(rows);
    });
});


https.createServer(options, registry).listen(port, () => {
    console.log(`API EV_Registry (HTTPS) ejecutándose en puerto ${port}`);
});
