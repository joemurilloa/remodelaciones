from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from models import db, Cliente, Cotizacion, Factura, ItemCotizacion, ItemFactura
import pdf_generator
import backup_drive


app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_para_desarrollo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_cotizaciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'pdfs')

# Asegurar que exista la carpeta para PDFs
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar la base de datos
db.init_app(app)

# Crear todas las tablas si no existen
with app.app_context():
    db.create_all()

# Rutas para la página principal
@app.route('/')
def home():
    return render_template('home.html')

# Rutas para clientes
@app.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes/listar.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        rut = request.form['rut']
        
        nuevo_cliente = Cliente(nombre=nombre, email=email, telefono=telefono, 
                              direccion=direccion, rut=rut)
        db.session.add(nuevo_cliente)
        db.session.commit()
        flash('Cliente agregado correctamente')
        return redirect(url_for('listar_clientes'))
    
    return render_template('clientes/nuevo.html')

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.email = request.form['email']
        cliente.telefono = request.form['telefono']
        cliente.direccion = request.form['direccion']
        cliente.rut = request.form['rut']
        
        db.session.commit()
        flash('Cliente actualizado correctamente')
        return redirect(url_for('listar_clientes'))
    
    return render_template('clientes/editar.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado correctamente')
    return redirect(url_for('listar_clientes'))

# Rutas para cotizaciones
@app.route('/cotizaciones')
def listar_cotizaciones():
    cotizaciones = Cotizacion.query.all()
    return render_template('cotizaciones/listar.html', cotizaciones=cotizaciones)

@app.route('/cotizaciones/nueva', methods=['GET', 'POST'])
def nueva_cotizacion():
    clientes = Cliente.query.all()
    now = datetime.now()
    
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        validez = int(request.form['validez'])
        descripcion = request.form['descripcion']
        
        nueva_cotizacion = Cotizacion(
            cliente_id=cliente_id,
            fecha=fecha,
            validez=validez,
            descripcion=descripcion
        )
        
        db.session.add(nueva_cotizacion)
        db.session.commit()
        
        # Procesar items
        nombres = request.form.getlist('item_nombre[]')
        cantidades = request.form.getlist('item_cantidad[]')
        precios = request.form.getlist('item_precio[]')
        
        for i in range(len(nombres)):
            if nombres[i]:  # Solo procesar si hay un nombre
                item = ItemCotizacion(
                    cotizacion_id=nueva_cotizacion.id,
                    nombre=nombres[i],
                    cantidad=int(cantidades[i]),
                    precio_unitario=float(precios[i])
                )
                db.session.add(item)
        
        db.session.commit()
        
        # Generar PDF
        pdf_filename = pdf_generator.generar_pdf_cotizacion(nueva_cotizacion)
        
        flash('Cotización creada correctamente')
        return redirect(url_for('ver_cotizacion', id=nueva_cotizacion.id))
    
        return render_template('cotizaciones/nueva.html', clientes=clientes, now=now)


@app.route('/cotizaciones/ver/<int:id>')
def ver_cotizacion(id):
    cotizacion = Cotizacion.query.get_or_404(id)
    pdf_filename = f"cotizacion_{cotizacion.id}.pdf"
    return render_template('cotizaciones/ver.html', cotizacion=cotizacion, pdf_filename=pdf_filename)

@app.route('/cotizaciones/pdf/<int:id>')
def pdf_cotizacion(id):
    cotizacion = Cotizacion.query.get_or_404(id)
    pdf_filename = f"cotizacion_{cotizacion.id}.pdf"
    
    # Si el PDF no existe, generarlo
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    if not os.path.exists(pdf_path):
        pdf_generator.generar_pdf_cotizacion(cotizacion)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], pdf_filename)

@app.route('/cotizaciones/a-factura/<int:id>')
def cotizacion_a_factura(id):
    cotizacion = Cotizacion.query.get_or_404(id)
    
    # Crear nueva factura basada en la cotización
    nueva_factura = Factura(
        cliente_id=cotizacion.cliente_id,
        cotizacion_id=cotizacion.id,
        fecha=datetime.now(),
        descripcion=f"Factura basada en cotización #{cotizacion.id}"
    )
    
    db.session.add(nueva_factura)
    db.session.commit()
    
    # Copiar items de la cotización a la factura
    for item_cotizacion in cotizacion.items:
        item_factura = ItemFactura(
            factura_id=nueva_factura.id,
            nombre=item_cotizacion.nombre,
            cantidad=item_cotizacion.cantidad,
            precio_unitario=item_cotizacion.precio_unitario
        )
        db.session.add(item_factura)
    
    db.session.commit()
    
    # Generar PDF de la factura
    pdf_generator.generar_pdf_factura(nueva_factura)
    
    flash('Cotización convertida a factura correctamente')
    return redirect(url_for('ver_factura', id=nueva_factura.id))

# Rutas para facturas
@app.route('/facturas')
def listar_facturas():
    facturas = Factura.query.all()
    return render_template('facturas/listar.html', facturas=facturas)

@app.route('/facturas/ver/<int:id>')
def ver_factura(id):
    factura = Factura.query.get_or_404(id)
    pdf_filename = f"factura_{factura.id}.pdf"
    return render_template('facturas/ver.html', factura=factura, pdf_filename=pdf_filename)

@app.route('/facturas/pdf/<int:id>')
def pdf_factura(id):
    factura = Factura.query.get_or_404(id)
    pdf_filename = f"factura_{factura.id}.pdf"
    
    # Si el PDF no existe, generarlo
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    if not os.path.exists(pdf_path):
        pdf_generator.generar_pdf_factura(factura)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], pdf_filename)

# Ruta para iniciar backup manual
@app.route('/backup')
def realizar_backup():
    try:
        backup_file = backup_drive.realizar_backup()
        backup_drive.subir_a_drive(backup_file)
        flash('Backup realizado correctamente')
    except Exception as e:
        flash(f'Error al realizar el backup: {str(e)}')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)