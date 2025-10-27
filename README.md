# PFO3 – Sistema Distribuido (Cliente-Servidor con Sockets)

Este repositorio implementa un sistema distribuido con arquitectura **Cliente → Balanceador (Nginx) → Múltiples Servidores Worker**.

El objetivo es procesar tareas de manera paralela mediante sockets TCP y un pool de hilos.

## Contenido del Repositorio

- **Diagrama de arquitectura** (Mermaid y PlantUML) en `diagrams/`
- **Servidor** con sockets y threads: `server.py`
- **Cliente** que envía tareas y recibe resultados: `client.py`
- **Configuración de balanceo TCP** con Nginx: `conf/nginx.conf`
- (Opcional) **RabbitMQ** integrado a nivel de código, no usado en esta versión de pruebas

---

## Arquitectura

- Clientes (web/móvil)
- **Nginx** como balanceador de carga (TCP stream)
- 3 servidores workers en puertos 9001, 9002 y 9003
- Comunicación por sockets
- Procesamiento paralelo mediante threads

> "Balanceador de carga (Nginx/HAProxy)"



## 🖥️ Ejecución del Sistema

 Ejecución sin RabbitMQ para pruebas locales

### 1️⃣ Iniciar los servidores workers

Abrir **tres** terminales en:

C:\Users\Manu\OneDrive\Escritorio\pfo3-distribuido

bash
Copiar código

Y ejecutar:

``bash
# Ventana 1
set SERVER_PORT=9001 && python server.py

# Ventana 2
set SERVER_PORT=9002 && python server.py

# Ventana 3
set SERVER_PORT=9003 && python server.py
Verificar puertos escuchando:

bash
Copiar código
netstat -ano | findstr :9001
netstat -ano | findstr :9002
netstat -ano | findstr :9003
✅ Los tres deben estar en estado LISTENING

2️⃣ Iniciar Nginx como balanceador
Ruta donde fue instalado:

Copiar código
C:\Users\Manu\OneDrive\Documentos\Ngnix\nginx-1.29.2

Probar sintaxis:

bash
Copiar código
nginx -t
Recargar (o iniciar si no está corriendo):

bash
Copiar código
nginx -s reload
# o si estaba apagado
nginx
Verificar puerto 9000:

bash
Copiar código
netstat -ano | findstr :9000
✅ Debe decir LISTENING

3️⃣ Enviar tareas desde el cliente
En otra terminal:

bash
Copiar código
cd C:\Users\Manu\OneDrive\Escritorio\pfo3-distribuido
python client.py 127.0.0.1 9000
📌 Nginx va a repartir las solicitudes entre 9001–9003
📌 En cada consola de servidor deben aparecer tareas recibidas
📌 El cliente debe mostrar respuestas status: done

Formato del mensaje JSON
Cada línea enviada:

json
Copiar código
{"id": 1, "action": "upper", "payload": "hola"}
Ejemplo de respuesta:

json
Copiar código
{"id":1,"status":"done","result":{"ok":true,"data":"HOLA"}}
Acciones demostración:

echo

upper

sleep

fib

📊 Diagramas del Sistema Distribuido
✅ Diagrama Mermaid (Arquitectura de Comunicación)


🔗 Versión interactiva:
https://mermaid.live/view#pako:eNqNlN1O4zAQhV_FMjdFW2jzQylehAStBCs1S6BISJtw4SSTNuDExXagLPBU-wj7YuskLimwqriKz_h8M56Jk2cc8wQwwSnjj_GcCoUml2GBkCyjmaCLORqxDAolg-YJ8qbaRcjjUcYgCLGJI-_vn4eMhfiGEBLXscZ4DdGaS6uPFiiSsKgWkxNtPKGMFjHQhAuUABpRMaOHkegddc6OfcGXT72fs6xYbjdZWNSgb6e95uIOhAx8zlnFT0E8ZDoXSLNljj-1dK0mgqwmv-TxHSj0Dam50PWlKSHFg0HsFrG_iDgt4nwFeZuFdxF0LmkUZcq7qMERZ7RqyINC0luQ2xWV339of0wVDY5ZTmMoaF5NmKNxJpXIolKPwTTvnwYdn0s1EzC9mNSZkmh14mnQmTo9Lyt-nNeFz6NbULypx6Pbd6c0dwPt7By9XI383tnVlf-i32PzNlfhFz3tTxH7U8Rpck4tdKiDegK1st8pp1XrXv903WuU0yrjraRu0HjXldOqZvqoTWSE2YwZlXIMKWouMEozxsgWQNrVU-Z3QLbceGDWO49ZoubEWiy_r4EsMlCaJm9QGvU3Qvp-rEql0Jai7kYqv1-VghaK3c1QEv2nKWcQb4T0zfg6hbt4JrIEEyVK6OIcRE4riZ-reYdYzSGHEBO9TCClJVMhDotXjS1o8YvzfEUKXs7mmKSUSa3KRUIVjDOqv4XWoi8riBEvC4XJXp0Bk2e8xGTg7g739_r2cGD194eO63TxEyaWY-86B_u26xy4_aFruYPXLv5d1-xX_i6GJFNceM1vs_57vv4D3MuxTA

✅ Diagrama PlantUML (Vista estructural)



🔗 Versión online:
https://www.plantuml.com/plantuml/png/TP3HJi8m58Rl-nJDhZ264DPROm0JqOJXS1UxyUPiEs13rs9xPk2vV0HVp7QaKqouwjV-tz_cTEO8B7MjOculzG4ijBp1BNIA7escDRJ8vrR2txmsxS5er5JGII6tM1FedKB6e2PZUVAWf4-HbrWb75nO_qVPzzUdL7sQcKg6yd0FJnQWGDS8ZQ-CdkQvDSVJPBsJ-dZJLrOBfatZnTBOFLe-VTCZP-ez4h_bz6vzqvtDSdfffjVDzD8Krqt1s4U7dNTVeQeaPPlp81lM0445pYUvSRIpM6nMVPOlsTQe1YrF2Z79f7v-wSyBmLY95H-FxyDKvx-8ExPQ10n3H4e72iKfl_CS7YxJNnG31YDWlWn2914fneK8SIGHYSrGDrshVW00


Conclusión
Este sistema distribuido:
✅ Soporta múltiples clientes
✅ Balancea carga entre distintos servidores
✅ Procesa en paralelo usando threads
✅ Mantiene independencia entre componentes


Autor
Manuel Correderas
PFO3 – Programación sobre redes 3D – IFTS Nº29