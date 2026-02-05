# assistant_bot.py
from typing import List, Dict, Any

from nlp_parser import parse_user_message
from iata_service import build_final_json


def asistent(nombre_empresa: str = "Nombre_empresa") -> List[Dict[str, Any]]:
    print(f"Hola, bienvenido a {nombre_empresa}. ¿Como te puedo ayudar?")

    logs: List[Dict[str, Any]] = []

    while True:
        user_msg = input("> ").strip()
        if user_msg.lower() == "salir":
            print("¡Listo! Conversación finalizada.")
            return logs

        parsed = parse_user_message(user_msg)

        faltantes = []
        if not parsed.get("origen"):
            faltantes.append("origen")
        if not parsed.get("destino"):
            faltantes.append("destino")
        if not parsed.get("fecha"):
            faltantes.append("fecha")
        if not parsed.get("aerolínea"):
            faltantes.append("aerolínea")

        if faltantes:
            for f in faltantes:
                if f == "origen":
                    print("No pude detectar el ORIGEN. Ej: 'de Quito a Madrid ...'")
                elif f == "destino":
                    print("No pude detectar el DESTINO. Ej: '... a Madrid ...'")
                elif f == "fecha":
                    print("No pude detectar la FECHA. Ej: '... para el 15 de octubre' o '... en septiembre'")
                elif f == "aerolínea":
                    print("No pude detectar la AEROLÍNEA. Ej: '... con Iberia' o '... Lufthansa'")

            print("Corrige el mensaje y vuelve a intentarlo. (No se generó JSON final)\n")
            continue

        try:
            final_json = build_final_json(parsed)
        except Exception as e:
            print("⚠️ Hubo un problema técnico consultando códigos IATA.")
            print(f"Detalle: {e}\n")
            continue

        origen = final_json.get("Ciudad Origen")
        destino = final_json.get("Ciudad Destino")
        fecha = final_json.get("Fecha")
        aerolinea = final_json.get("Aerolínea")

        print(f"Perfecto, Comienzo la búsqueda de tu viaje a {destino} desde {origen} para el {fecha} con {aerolinea}.")
        print("\nJSON final:")
        print(final_json)

        logs.append(final_json)
        print("\nEscribe otra solicitud o 'salir' para terminar.")


if __name__ == "__main__":
    asistent("Nombre_empresa")