# Entorno de virtualización Python

# Pasos de instalación en Linux:

## 1. Clonación del proyecto

Desde la terminal ejecutar:

**git clone** <URL_del_repositorio> <nombre_de_la_carpeta_de_destino>

Luego ejecutar **cd** <nombre_de_la_carpeta_de_destino>. Esta carpeta será la raíz de nuestro proyecto en Python.

## 2. Creación del entorno virtual

Supongamos que el nombre que le damos al entorno virtual es **cisco**, entonces se creará una carpeta **cisco** con todas las librerías y dependencias necesarias paea nuestro proyecto. 

La manera de realizarlo es la siguiente:

# python3 -m venv <nombre_del_entorno>
Ejemplo: python3 -m venv cisco

Para activar el entorno escribimos **source cisco/bin/activate**, en la carpeta raíz del proyecto. El nombre del entorno virtual aparecerá entre paréntesis ().

## 3. Instalación de las dependencias, en este caso las librerías requests y tabulate

En la carpeta raíz de nuestro proyecto y dentro del entorno virtual escribimos: **pip install -r requirements.txt**

## 4. Selección del intérprete Python para nuestro entorno virtual

<img width="881" height="118" alt="image" src="https://github.com/user-attachments/assets/18c41d8e-d338-48b6-953c-b2499c57319f" />

<img width="736" height="412" alt="image" src="https://github.com/user-attachments/assets/2a795fcd-2cf8-47ef-a5a6-d21e09ce967f" />

Tal como se ve en la figura seleccionamos Python 3.10.12 (cisco) que se mostrará como entorno recomendado.

## 5. Desactivación del entorno virtual

Simplemente escribimos en la línea de comandos: **deactivate**



## Antes de ejecutar los scripts

- **Credenciales del controlador:** los scripts usan el usuario `cisco` y la clave `cisco123!`. Si en tu Network Controller creaste otro usuario, cambialos en `01_get-ticket.py` y en `04_tabulate.py`.
- **Ticket (X-Auth-Token):** `02_get-network-device.py` y `03_get-host.py` traen escrito un ticket de ejemplo que **no va a funcionar** en tu Packet Tracer, porque el controlador genera uno nuevo en cada sesión y vence. Ejecutá primero `01_get-ticket.py`, copiá el ticket que muestra y reemplazalo en el header `X-Auth-Token` de esos dos scripts. `04_tabulate.py` no necesita este paso: pide el ticket solo.


---

# Grupo 01 – TP N° 4 Integrador (Redes de Computadoras 3643)

Scripts usados para verificar la API Northbound del Network Controller de Packet Tracer (`http://localhost:58000/api/v1`, con el acceso externo habilitado en el controlador).

## Qué hace cada script

| Script | Qué hace |
|---|---|
| `src/01_get-ticket.py` | Pide un ticket de sesión al controlador (`POST /ticket`) y lo muestra. |
| `src/02_get-network-device.py` | Lista los equipos de red gestionados (`GET /network-device`): hostname, plataforma e IP de gestión. Necesita un ticket vigente en `X-Auth-Token`. |
| `src/03_get-host.py` | Lista los hosts detectados (`GET /host`): nombre, IP, MAC e interfaz. Necesita un ticket vigente en `X-Auth-Token`. |
| `src/04_tabulate.py` | Pide el ticket solo y muestra equipos y hosts en tablas con la librería `tabulate`. |
| `src/05_inventario_csv.py` | **Script propio.** Arma un inventario completo de la red y lo exporta a CSV (ver abajo). |

## Script propio: `05_inventario_csv.py`

Genera un inventario de la red a partir del controlador y lo guarda en la carpeta `salida/`:

- `inventario_equipos.csv`: hostname, tipo, plataforma, IP de gestión, versión de IOS, número de serie y estado de cada equipo.
- `inventario_hosts.csv`: nombre, tipo, IP y MAC de cada host, junto con **el equipo y la interfaz a la que está conectado** (cruza los datos de `/host` con los de `/network-device`).

Por pantalla muestra las dos tablas y un resumen: cantidad de equipos por tipo, aviso si algún equipo no está en estado `Managed` y cantidad de hosts por equipo.

Respecto de los scripts suministrados, además:

- pide el ticket solo y **cierra la sesión** al terminar (`DELETE /ticket/{ticket}`);
- **no tiene usuario ni clave en el código**: los toma de las variables de entorno `NC_USER` y `NC_PASS` o los pide por teclado, porque el repositorio es público;
- informa errores claros si no hay conexión con el controlador o si las credenciales son incorrectas.

Uso (con el entorno virtual activado):

```
python src/05_inventario_csv.py
```

La URL del controlador se puede cambiar con la variable de entorno `NC_URL` (por defecto `http://localhost:58000/api/v1`). Los CSV usan `;` como separador y se abren directamente en Excel o LibreOffice.

## Entorno en Windows

```
py -m venv cisco
.\cisco\Scripts\activate
pip install -r requirements.txt
```
