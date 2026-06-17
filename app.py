from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import requests
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

TOKEN = "8898420539:AAFbZBdmKeV-QGbqz4PnPrH6Wmud8QtgDgM"
CHAT_ID = "8800367561"

# ------------------------
# TABLA DE REGISTROS
# ------------------------
class Registro(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    temperatura = db.Column(
        db.Float
    )

    humedad = db.Column(
        db.Float
    )

    fecha = db.Column(
        db.String(50)
    )


# ------------------------
# TABLA DE ALERTAS
# ------------------------
class Alerta(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    tipo = db.Column(
        db.String(100)
    )

    fecha = db.Column(
        db.String(50)
    )
def enviar_telegram(mensaje):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": mensaje
        }
    )
    
@app.route("/telegram")
def telegram():

    enviar_telegram(
        "✅ Prueba de Telegram desde Render"
    )

    return "Mensaje enviado"


@app.route("/")
def inicio():

    ultimo = Registro.query.order_by(
        Registro.id.desc()
    ).first()

    if ultimo:

        temperatura = ultimo.temperatura
        humedad = ultimo.humedad

    else:

        temperatura = 0
        humedad = 0

    registros = Registro.query.order_by(
        Registro.id.desc()
    ).limit(10).all()

    registros.reverse()

    alertas = Alerta.query.order_by(
        Alerta.id.desc()
    ).limit(10).all()

    if len(registros) > 0:

        prom_temp = round(
            sum(r.temperatura for r in registros) / len(registros),
            1
        )

        prom_hum = round(
            sum(r.humedad for r in registros) / len(registros),
            1
        )

    else:

        prom_temp = 0
        prom_hum = 0

    total_alertas = Alerta.query.count()

    alerta = ""

    if temperatura > 15:
        alerta += "⚠ Temperatura alta<br>"

    if temperatura < 5:
        alerta += "⚠ Temperatura baja<br>"

    if humedad > 85:
        alerta += "⚠ Humedad alta<br>"

    if humedad < 60:
        alerta += "⚠ Humedad baja<br>"

    estado = "🟢 ESTABLE"

    if temperatura > 15 or humedad > 85:
        estado = "🔴 CRÍTICO"

    elif temperatura < 5 or humedad < 60:
        estado = "🟡 PRECAUCIÓN"

    return render_template(
        "index.html",
        temperatura=temperatura,
        humedad=humedad,
        alerta=alerta,
        registros=registros,
        alertas=alertas,
        prom_temp=prom_temp,
        prom_hum=prom_hum,
        total_alertas=total_alertas,
        estado=estado
    )

@app.route("/api/sensores", methods=["POST"])
def recibir_datos():

    datos = request.get_json()

    temperatura = datos["temperatura"]
    humedad = datos["humedad"]

    fecha = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    nuevo = Registro(
        temperatura=temperatura,
        humedad=humedad,
        fecha=fecha
    )

    db.session.add(nuevo)

    if temperatura > 15:

        db.session.add(
            Alerta(
                tipo="Temperatura Alta",
                fecha=fecha
            )
        )
        enviar_telegram(
            f"⚠ ALERTA\nTemperatura Alta\n{temperatura} °C\n{fecha}"
        )

    if temperatura < 5:

        db.session.add(
            Alerta(
                tipo="Temperatura Baja",
                fecha=fecha
            )
        )
        enviar_telegram(
            f"⚠ ALERTA\nTemperatura Baja\n{temperatura} °C\n{fecha}"
        )

    if humedad > 85:

        db.session.add(
            Alerta(
                tipo="Humedad Alta",
                fecha=fecha
            )
        )
        enviar_telegram(
            f"⚠ ALERTA\nHumedad Alta\n{humedad}%\n{fecha}"
        )

    if humedad < 60:

        db.session.add(
            Alerta(
                tipo="Humedad Baja",
                fecha=fecha
            )
        )
        enviar_telegram(
            f"⚠ ALERTA\nHumedad Baja\n{humedad}%\n{fecha}"
        )

    db.session.commit()

    return jsonify({
        "mensaje": "Datos recibidos correctamente"
    })

@app.route("/simular", methods=["POST"])
def simular():

    temperatura = float(
        request.form["temperatura"]
    )

    humedad = float(
        request.form["humedad"]
    )

    fecha = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    nuevo = Registro(
        temperatura=temperatura,
        humedad=humedad,
        fecha=fecha
    )

    db.session.add(nuevo)

    if temperatura > 15:

        db.session.add(
            Alerta(
                tipo="Temperatura Alta",
                fecha=fecha
            )
        )
        enviar_telegram(
            f"⚠ ALERTA\nTemperatura Alta\n{temperatura} °C\n{fecha}"
        )

    if temperatura < 5:

        db.session.add(
            Alerta(
                tipo="Temperatura Baja",
                fecha=fecha
            )
        )
        enviar_telegram(
            f"⚠ ALERTA\nTemperatura Baja\n{temperatura} °C\n{fecha}"
        )

    if humedad > 85:

        db.session.add(
            Alerta(
                tipo="Humedad Alta",
                fecha=fecha
            )
        )
       enviar_telegram(
            f"⚠ ALERTA\nHumedad Alta\n{humedad}%\n{fecha}"
        )

    if humedad < 60:

        db.session.add(
            Alerta(
                tipo="Humedad Baja",
                fecha=fecha
            )
        )
       enviar_telegram(
            f"⚠ ALERTA\nHumedad Baja\n{humedad}%\n{fecha}"
        )

    db.session.commit()

    return redirect("/")


@app.route("/reporte")
def reporte():

    registros = Registro.query.order_by(
        Registro.id.desc()
    ).limit(20).all()

    total_alertas = Alerta.query.count()

    if len(registros) > 0:

        prom_temp = round(
            sum(r.temperatura for r in registros) / len(registros),
            1
        )

        prom_hum = round(
            sum(r.humedad for r in registros) / len(registros),
            1
        )

    else:

        prom_temp = 0
        prom_hum = 0

    pdf = SimpleDocTemplate(
        "reporte_agroexportadora.pdf"
    )

    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph(
            "REPORTE DEL ALMACEN DE FRUTAS",
            estilos["Title"]
        )
    )

    elementos.append(Spacer(1,20))

    elementos.append(
        Paragraph(
            f"Fecha: {datetime.now()}",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Temperatura Promedio: {prom_temp} °C",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Humedad Promedio: {prom_hum} %",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Total Alertas: {total_alertas}",
            estilos["Normal"]
        )
    )

    elementos.append(Spacer(1,20))

    datos_tabla = [
        ["ID","Temperatura","Humedad","Fecha"]
    ]

    for r in registros:

        datos_tabla.append([
            r.id,
            r.temperatura,
            r.humedad,
            r.fecha
        ])

    tabla = Table(datos_tabla)

    tabla.setStyle(

        TableStyle([

            ('BACKGROUND',(0,0),(-1,0),colors.grey),

            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),

            ('GRID',(0,0),(-1,-1),1,colors.black)

        ])

    )

    elementos.append(tabla)

    pdf.build(elementos)

    return """
    <h2>Reporte generado correctamente</h2>
    <a href='/'>Volver al Dashboard</a>
    """

@app.route("/auto", methods=["POST"])
def auto():

    import random

    for i in range(20):

        temperatura = round(
            random.uniform(3, 20),
            1
        )

        humedad = round(
            random.uniform(50, 95),
            1
        )

        fecha = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        nuevo = Registro(
            temperatura=temperatura,
            humedad=humedad,
            fecha=fecha
        )

        db.session.add(nuevo)

        if temperatura > 15:
            db.session.add(
                Alerta(
                    tipo="Temperatura Alta",
                    fecha=fecha
                )
            )
            enviar_telegram(
                f"⚠ ALERTA\nTemperatura Alta\n{temperatura} °C\n{fecha}"
            )

        if temperatura < 5:
            db.session.add(
                Alerta(
                    tipo="Temperatura Baja",
                    fecha=fecha
                )
            )
            enviar_telegram(
                f"⚠ ALERTA\nTemperatura Baja\n{temperatura} °C\n{fecha}"
            )

        if humedad > 85:
            db.session.add(
                Alerta(
                    tipo="Humedad Alta",
                    fecha=fecha
                )
            )
            enviar_telegram(
                f"⚠ ALERTA\nHumedad Alta\n{humedad}%\n{fecha}"
            )

        if humedad < 60:
            db.session.add(
                Alerta(
                    tipo="Humedad Baja",
                    fecha=fecha
                )
            )
            enviar_telegram(
                f"⚠ ALERTA\nHumedad Baja\n{humedad}%\n{fecha}"
            )
            

    db.session.commit()

    return redirect("/")

with app.app_context():
    print("CREANDO TABLAS...")
    db.create_all()
    print("TABLAS CREADAS")

if __name__ == "__main__":
    app.run(debug=True)
