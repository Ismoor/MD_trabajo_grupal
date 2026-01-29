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
        final_json = build_final_json(parsed)

        origen = final_json.get("Ciudad Origen")
        destino = final_json.get("Ciudad Destino")
        fecha = final_json.get("Fecha")
        iata_from = final_json.get("IATA From")
        iata_to = final_json.get("IATA To")
        pax = final_json.get("Pax")

        print(
            f"Perfecto: {origen} ({iata_from}) -> {destino} ({iata_to}), "
            f"Fecha: {fecha}, Pax: {pax}."
        )

        print("\nJSON final:")
        print(final_json)

        logs.append(final_json)
        print("\nEscribe otra solicitud o 'salir' para terminar.")


if __name__ == "__main__":
    asistent("Nombre_empresa")