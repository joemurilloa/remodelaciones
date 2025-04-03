from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    rut = db.Column(db.String(20), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    cotizaciones = db.relationship('Cotizacion', backref='cliente', lazy=True)
    facturas = db.relationship('Factura', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'rut': self.rut
        }

class Cotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    validez = db.Column(db.Integer, default=30)  # Días de validez
    descripcion = db.Column(db.Text, nullable=True)
    
    # Relaciones
    items = db.relationship('ItemCotizacion', backref='cotizacion', lazy=True, cascade="all, delete-orphan")
    facturas = db.relationship('Factura', backref='cotizacion', lazy=True)
    
    def __repr__(self):
        return f'<Cotizacion #{self.id}>'
    
    @property
    def fecha_vencimiento(self):
        return self.fecha + timedelta(days=self.validez)
    
    @property
    def esta_vencida(self):
        return datetime.now() > self.fecha_vencimiento
    
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items)
    
    @property
    def iva(self):
        return self.subtotal * 0.19  # 19% IVA en Chile
    
    @property
    def total(self):
        return self.subtotal + self.iva

class ItemCotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizacion.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<ItemCotizacion {self.nombre}>'
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizacion.id'), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    pagada = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    items = db.relationship('ItemFactura', backref='factura', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Factura #{self.id}>'
    
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items)
    
    @property
    def iva(self):
        return self.subtotal * 0.19  # 19% IVA en Chile
    
    @property
    def total(self):
        return self.subtotal + self.iva

class ItemFactura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('factura.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<ItemFactura {self.nombre}>'
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario