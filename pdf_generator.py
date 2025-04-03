from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime
import locale

# Configurar el locale para formato de números en español
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
    except:
        pass  # Si falla, usamos el locale por defecto

def formato_moneda(valor):
    return f"${valor:,.0f}"

def generar_pdf_cotizacion(cotizacion):
    # Crear directorio para PDFs si no existe
    pdf_dir = os.path.join('static', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Configurar el documento
    filename = os.path.join(pdf_dir, f"cotizacion_{cotizacion.id}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    
    # Título
    title = Paragraph(f"<font size='16'><b>COTIZACIÓN #{cotizacion.id}</b></font>", styles['Center'])
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))
    
    # Información del cliente y fecha
    data = [
        ["DATOS EMPRESA", "DATOS CLIENTE"],
        ["Tu Empresa SPA", f"Nombre: {cotizacion.cliente.nombre}"],
        ["RUT: 76.XXX.XXX-X", f"RUT: {cotizacion.cliente.rut or 'No especificado'}"],
        ["Dirección: Tu dirección", f"Dirección: {cotizacion.cliente.direccion or 'No especificada'}"],
        ["Teléfono: +56 9 XXXX XXXX", f"Teléfono: {cotizacion.cliente.telefono or 'No especificado'}"],
        ["Email: contacto@tuempresa.cl", f"Email: {cotizacion.cliente.email or 'No especificado'}"]
    ]
    
    # Crear tabla de datos
    info_table = Table(data, colWidths=[doc.width/2.0]*2)
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Fecha y validez
    fecha_formato = cotizacion.fecha.strftime("%d/%m/%Y")
    fecha_vencimiento = cotizacion.fecha_vencimiento.strftime("%d/%m/%Y")
    
    fecha_info = [
        ["Fecha de emisión:", fecha_formato],
        ["Válida hasta:", fecha_vencimiento]
    ]
    
    fecha_table = Table(fecha_info, colWidths=[doc.width/4.0, doc.width/4.0])
    fecha_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(fecha_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Descripción de la cotización
    if cotizacion.descripcion:
        elements.append(Paragraph("<b>Descripción:</b>", styles['Normal']))
        elements.append(Paragraph(cotizacion.descripcion, styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
    
    # Items de la cotización
    elements.append(Paragraph("<b>Detalle de la cotización:</b>", styles['Normal']))
    
    # Cabecera de la tabla de items
    items_data = [['Ítem', 'Cantidad', 'Precio Unitario', 'Subtotal']]
    
    # Añadir los items
    for item in cotizacion.items:
        items_data.append([
            item.nombre,
            str(item.cantidad),
            formato_moneda(item.precio_unitario),
            formato_moneda(item.subtotal)
        ])
    
    # Añadir totales
    items_data.append(['', '', '<b>Subtotal:</b>', formato_moneda(cotizacion.subtotal)])
    items_data.append(['', '', '<b>IVA (19%):</b>', formato_moneda(cotizacion.iva)])
    items_data.append(['', '', '<b>TOTAL:</b>', formato_moneda(cotizacion.total)])
    
    # Crear tabla de items
    items_table = Table(items_data, colWidths=[doc.width*0.4, doc.width*0.1, doc.width*0.25, doc.width*0.25])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (3, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('LINEBELOW', (2, -3), (3, -1), 1, colors.black),
    ]))
    elements.append(items_table)
    
    # Notas finales
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("<b>Notas:</b>", styles['Normal']))
    elements.append(Paragraph("1. Esta cotización tiene validez hasta la fecha indicada.", styles['Normal']))
    elements.append(Paragraph("2. Los precios pueden variar sin previo aviso después de la fecha de vencimiento.", styles['Normal']))
    elements.append(Paragraph("3. Forma de pago: Transferencia bancaria o efectivo.", styles['Normal']))
    
    # Generar el PDF
    doc.build(elements)
    
    return f"cotizacion_{cotizacion.id}.pdf"

def generar_pdf_factura(factura):
    # Crear directorio para PDFs si no existe
    pdf_dir = os.path.join('static', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Configurar el documento
    filename = os.path.join(pdf_dir, f"factura_{factura.id}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    
    # Título
    title = Paragraph(f"<font size='16'><b>FACTURA #{factura.id}</b></font>", styles['Center'])
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))
    
    # Información del cliente y fecha
    data = [
        ["DATOS EMPRESA", "DATOS CLIENTE"],
        ["Tu Empresa SPA", f"Nombre: {factura.cliente.nombre}"],
        ["RUT: 76.XXX.XXX-X", f"RUT: {factura.cliente.rut or 'No especificado'}"],
        ["Dirección: Tu dirección", f"Dirección: {factura.cliente.direccion or 'No especificada'}"],
        ["Teléfono: +56 9 XXXX XXXX", f"Teléfono: {factura.cliente.telefono or 'No especificado'}"],
        ["Email: contacto@tuempresa.cl", f"Email: {factura.cliente.email or 'No especificado'}"]
    ]
    
    # Crear tabla de datos
    info_table = Table(data, colWidths=[doc.width/2.0]*2)
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Fecha e información de cotización relacionada
    fecha_formato = factura.fecha.strftime("%d/%m/%Y")
    
    fecha_info = [
        ["Fecha de emisión:", fecha_formato],
    ]
    
    if factura.cotizacion:
        fecha_info.append(["Basada en cotización:", f"#{factura.cotizacion.id}"])
    
    fecha_table = Table(fecha_info, colWidths=[doc.width/4.0, doc.width/4.0])
    fecha_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(fecha_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Descripción de la factura
    if factura.descripcion:
        elements.append(Paragraph("<b>Descripción:</b>", styles['Normal']))
        elements.append(Paragraph(factura.descripcion, styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
    
    # Items de la factura
    elements.append(Paragraph("<b>Detalle de la factura:</b>", styles['Normal']))
    
    # Cabecera de la tabla de items
    items_data = [['Ítem', 'Cantidad', 'Precio Unitario', 'Subtotal']]
    
    # Añadir los items
    for item in factura.items:
        items_data.append([
            item.nombre,
            str(item.cantidad),
            formato_moneda(item.precio_unitario),
            formato_moneda(item.subtotal)
        ])
    
    # Añadir totales
    items_data.append(['', '', '<b>Subtotal:</b>', formato_moneda(factura.subtotal)])
    items_data.append(['', '', '<b>IVA (19%):</b>', formato_moneda(factura.iva)])
    items_data.append(['', '', '<b>TOTAL:</b>', formato_moneda(factura.total)])
    
    # Crear tabla de items
    items_table = Table(items_data, colWidths=[doc.width*0.4, doc.width*0.1, doc.width*0.25, doc.width*0.25])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (3, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('LINEBELOW', (2, -3), (3, -1), 1, colors.black),
    ]))
    elements.append(items_table)
    
    # Estado de pago
    elements.append(Spacer(1, 0.25*inch))
    estado_pago = "PAGADA" if factura.pagada else "PENDIENTE DE PAGO"
    estado_style = 'Heading2'
    estado_color = colors.green if factura.pagada else colors.red
    
    estado_paragraph = Paragraph(f"<font color={estado_color}><b>{estado_pago}</b></font>", styles[estado_style])
    elements.append(estado_paragraph)
    
    # Datos bancarios
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("<b>Datos de pago:</b>", styles['Normal']))
    elements.append(Paragraph("Banco: Banco Ejemplo", styles['Normal']))
    elements.append(Paragraph("Tipo de cuenta: Corriente", styles['Normal']))
    elements.append(Paragraph("Número de cuenta: 000-0-000000-0", styles['Normal']))
    elements.append(Paragraph("RUT: 76.XXX.XXX-X", styles['Normal']))
    elements.append(Paragraph("Titular: Tu Empresa SPA", styles['Normal']))
    elements.append(Paragraph("Email: pagos@tuempresa.cl", styles['Normal']))
    
    # Notas finales
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("<b>Notas:</b>", styles['Normal']))
    elements.append(Paragraph("1. Favor enviar comprobante de transferencia al email indicado.", styles['Normal']))
    elements.append(Paragraph("2. Esta factura es válida como comprobante tributario.", styles['Normal']))
    
    # Generar el PDF
    doc.build(elements)
    
    return f"factura_{factura.id}.pdf"