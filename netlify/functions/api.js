// Archivo de configuración para desplegar Flask en Netlify como función serverless

const serverless = require('serverless-http');
const express = require('express');
const path = require('path');
const { spawn } = require('child_process');

// Crear una app Express para manejar las solicitudes
const app = express();

// Configurar middleware para servir archivos estáticos
app.use('/static', express.static(path.join(__dirname, '../../static')));

// Configurar middleware para procesar solicitudes con Flask
app.all('*', (req, res) => {
  // Iniciar el proceso de Python
  const python = spawn('python', [path.join(__dirname, '../../app.py')]);
  
  // Manejar la salida de Python
  python.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });
  
  python.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });
  
  // Manejar la finalización del proceso
  python.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    if (code !== 0) {
      res.status(500).send('Error interno del servidor');
    }
  });
  
  // Enviar la solicitud a Flask
  const flaskApp = require('../../app');
  flaskApp.handle(req, res);
});

// Exportar la función serverless
module.exports.handler = serverless(app);