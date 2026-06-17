import requests
import random
import time

while True:

    datos = {
        "temperatura": round(
            random.uniform(3,20),
            1
        ),
        "humedad": round(
            random.uniform(50,95),
            1
        )
    }

    try:

        respuesta = requests.post(
            "http://127.0.0.1:5000/api/sensores",
            json=datos
        )

        print(
            "Enviado:",
            datos
        )

    except:

        print(
            "Servidor no disponible"
        )

    time.sleep(5)