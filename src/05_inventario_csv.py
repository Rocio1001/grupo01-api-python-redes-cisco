"""
05_inventario_csv.py - Script propio del Grupo 01 (TP4, Redes de Computadoras 3643)

Arma un inventario de la red a partir de la API Northbound del Network Controller
de Packet Tracer y lo exporta a dos archivos CSV:

  - inventario_equipos.csv : routers y switches que gestiona el controlador
  - inventario_hosts.csv   : hosts detectados, con el equipo y la interfaz a la que se conectan

Ademas muestra un resumen por pantalla: cuantos equipos hay de cada tipo, cuales no
estan en estado "Managed" y cuantos hosts cuelgan de cada equipo.

Que agrega respecto de los scripts suministrados:
  - pide el ticket solo y cierra la sesion al terminar (DELETE /ticket/{ticket});
  - no tiene usuario ni clave escritos en el codigo: los toma de variables de entorno
    o los pide por teclado (el repositorio es publico);
  - cruza los datos de /host con /network-device para decir a que equipo esta conectado
    cada host, y guarda todo en CSV para abrirlo con Excel o LibreOffice.

Uso:
    python 05_inventario_csv.py

Variables de entorno opcionales:
    NC_URL   URL base de la API (por defecto http://localhost:58000/api/v1)
    NC_USER  usuario del controlador
    NC_PASS  clave del controlador
"""

import csv
import getpass
import os
import sys
from collections import Counter

import requests
from tabulate import tabulate

BASE_URL = os.environ.get("NC_URL", "http://localhost:58000/api/v1")
CARPETA_SALIDA = "salida"


def pedir_credenciales():
    """Toma usuario y clave de variables de entorno o los pide por teclado."""
    usuario = os.environ.get("NC_USER") or input("Usuario del controlador: ").strip()
    clave = os.environ.get("NC_PASS") or getpass.getpass("Clave del controlador: ")
    return usuario, clave


def obtener_ticket(usuario, clave):
    """POST /ticket: devuelve el serviceTicket para usar en X-Auth-Token."""
    resp = requests.post(
        f"{BASE_URL}/ticket",
        json={"username": usuario, "password": clave},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    if resp.status_code != 201:
        sys.exit(f"No se pudo obtener el ticket (HTTP {resp.status_code}): {resp.text}")
    return resp.json()["response"]["serviceTicket"]


def consultar(recurso, ticket):
    """GET de un recurso de la API; devuelve la lista que viene en 'response'."""
    resp = requests.get(f"{BASE_URL}/{recurso}", headers={"X-Auth-Token": ticket}, timeout=10)
    if resp.status_code != 200:
        sys.exit(f"Error al consultar /{recurso} (HTTP {resp.status_code}): {resp.text}")
    return resp.json().get("response", [])


def cerrar_sesion(ticket):
    """DELETE /ticket/{ticket}: invalida el ticket al terminar."""
    try:
        resp = requests.delete(
            f"{BASE_URL}/ticket/{ticket}",
            headers={"X-Auth-Token": ticket, "Content-Type": "application/json"},
            timeout=10,
        )
        return resp.status_code
    except requests.RequestException:
        return None


def nombre_por_ip(equipos):
    """Diccionario IP -> hostname, con todas las IP conocidas de cada equipo."""
    mapa = {}
    for e in equipos:
        ips = [e.get("managementIpAddress", "")] + list(e.get("ipAddresses", []) or [])
        for ip in ips:
            if ip:
                mapa[ip] = e.get("hostname", "")
    return mapa


def guardar_csv(nombre, encabezados, filas):
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    ruta = os.path.join(CARPETA_SALIDA, nombre)
    # utf-8-sig para que Excel muestre bien los acentos
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(encabezados)
        w.writerows(filas)
    return ruta


def main():
    print(f"Controlador: {BASE_URL}\n")
    usuario, clave = pedir_credenciales()

    try:
        ticket = obtener_ticket(usuario, clave)
    except requests.ConnectionError:
        sys.exit("No hay conexion con el controlador. Revisar que Packet Tracer este abierto "
                 "y que el acceso externo (Access Enabled, puerto 58000) este habilitado.")
    print("Ticket obtenido.\n")

    try:
        equipos = consultar("network-device", ticket)
        hosts = consultar("host", ticket)
    finally:
        estado = cerrar_sesion(ticket)

    # ---------- equipos ----------
    enc_eq = ["Hostname", "Tipo", "Plataforma", "IP de gestion", "Version", "Serie", "Estado"]
    filas_eq = sorted(
        [[e.get("hostname", ""), e.get("type", ""), e.get("platformId", ""),
          e.get("managementIpAddress", ""), e.get("softwareVersion", ""),
          e.get("serialNumber", ""), e.get("collectionStatus", "")] for e in equipos],
        key=lambda f: (f[1], f[0]),
    )

    # ---------- hosts ----------
    ip_a_equipo = nombre_por_ip(equipos)
    enc_h = ["Host", "Tipo", "IP", "MAC", "Conectado a", "Interfaz del equipo"]
    filas_h = []
    for h in hosts:
        ip_equipo = h.get("connectedNetworkDeviceIpAddress", "")
        filas_h.append([h.get("hostName", ""), h.get("hostType", ""), h.get("hostIp", ""),
                        h.get("hostMac", ""), ip_a_equipo.get(ip_equipo, ip_equipo),
                        h.get("connectedInterfaceName", "")])
    filas_h.sort(key=lambda f: (f[4], f[0]))

    # ---------- salida por pantalla ----------
    print(f"Equipos de red ({len(filas_eq)}):")
    print(tabulate(filas_eq, headers=enc_eq, tablefmt="rst"))
    print(f"\nHosts ({len(filas_h)}):")
    print(tabulate(filas_h, headers=enc_h, tablefmt="rst"))

    print("\nResumen:")
    for tipo, cant in Counter(f[1] for f in filas_eq).most_common():
        print(f"  {tipo}: {cant}")
    no_gestionados = [f[0] or f[3] for f in filas_eq if f[6] != "Managed"]
    if no_gestionados:
        print(f"  ATENCION - equipos que no estan en Managed: {', '.join(no_gestionados)}")
    else:
        print("  Todos los equipos estan en estado Managed.")
    for equipo, cant in sorted(Counter(f[4] for f in filas_h).items()):
        print(f"  Hosts conectados a {equipo}: {cant}")

    # ---------- CSV ----------
    r1 = guardar_csv("inventario_equipos.csv", enc_eq, filas_eq)
    r2 = guardar_csv("inventario_hosts.csv", enc_h, filas_h)
    print(f"\nArchivos generados: {r1} y {r2}")
    print(f"Sesion cerrada (DELETE /ticket): HTTP {estado}")


if __name__ == "__main__":
    main()
