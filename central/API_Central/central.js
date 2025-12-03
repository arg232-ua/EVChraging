const express = require("express"); 
const centralSD = express(); 
// Se define el puerto 
const port=3000; 
const mysql = require ("mysql"); 
const bodyParser = require("body-parser"); 
// Configuración de la conexión a la base de datos MySQL 
const connection = mysql.createConnection({ 
    host: 'localhost', 
    user:'sd_remoto', 
    password: '1234', 
    database:'evcharging' 
}); 

// Comprobar conexión a la base de datos 
connection.connect(error=> { 
    if (error) throw error; 
    console.log('Conexión a la base de datos evcharging correcta'); 
}); 

centralSD.get("/",(req, res) => { 
res.json({message:'Página de inicio de aplicación CENTRAL de SD'}) 
}); 

// Ejecutar la aplicacion 
centralSD.listen(port, () => { 
console.log(`Ejecutando la aplicación API REST de la central en el puerto 
${port}`); 
});

//

// Listado de todos los usuarios 
centralSD.get("/usuarios",(request, response) => { 
    console.log('Listado de todos los usuarios'); 
    const sql = 'SELECT * FROM conductor'; 
    connection.query(sql,(error,resultado)=>{ 
        if (error) throw error; 
        if (resultado.length > 0){ 
            response.json(resultado); 
        } else { 
            response.send('No hay resultados'); 
        } 
    }); 
}); 

// Obtener datos de un usuario 
centralSD.get("/usuarios/:id",(request, response) => { 
    console.log('Obtener datos de un usuario'); 
    const {id} = request.params; 
    const sql = `SELECT * FROM conductor WHERE id_conductor = ?`; 
    connection.query(sql, [id],(error,resultado)=>{ 
        if (error) throw error; 
        if (resultado.length > 0){ 
            response.json(resultado); 
        } else { 
            response.send('No hay resultados'); 
        } 
    }) 
}); 

//Para poder procesar los parámetros dentro de body como json 
centralSD.use(bodyParser.json()); 

// Añadir un nuevo usuario 
centralSD.post("/usuarios",(request, response) => { 
    console.log('Añadir nuevo usuario'); 
    const sql = 'INSERT INTO conductor SET ?'; 
        const usuarioObj = { 
            nombre: request.body.nombre, 
            apellidos: request.body.apellidos, 
            email_conductor: request.body.correo,
            telefono_conductor: request.body.telefono,
            dni_conductor: request.body.dni
        } 
        connection.query(sql,usuarioObj,error => { 
        if (error) throw error; 
        response.send('Usuario creado'); 
    });  
});

// 4.5
// Modificar un usuario 
centralSD.put("/usuarios/:id",(request, response) => { 
    console.log('Modificar usuario'); 
    const {id} = request.params; 
    const {nombre,apellidos, telefono, correo, dni} = request.body; 
    const sql = `UPDATE conductor SET nombre=?, apellidos=?, telefono_conductor=?, email_conductor=?, dni_conductor=? WHERE id_conductor=?`; 
    
    connection.query(sql, [nombre, apellidos, telefono, correo, dni, id], (error, results) => { 
        if (error) {
            console.error('Error en la consulta:', error);
            return response.status(500).send('Error al modificar usuario');
        }
        
        if (results.affectedRows === 0) {
            return response.status(404).send('Usuario no encontrado');
        }
        
        response.send('Usuario modificado correctamente'); 
    });  
});

// Borrar un usuario 
centralSD.delete("/usuarios/:id", (request, response) => { 
    console.log('Borrar usuario'); 
    const {id} = request.params; 
    const sql = `DELETE FROM conductor WHERE id_conductor = ?`; 
    
    connection.query(sql, [id], (error, results) => { 
        if (error) {
            console.error('Error al borrar usuario:', error);
            return response.status(500).send('Error al borrar usuario');
        }
        
        if (results.affectedRows === 0) {
            return response.status(404).send('Usuario no encontrado');
        }
        
        response.send('Usuario borrado correctamente'); 
    });  
});