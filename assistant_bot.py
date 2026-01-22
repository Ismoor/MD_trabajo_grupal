# assistant_bot.py
from typing import List, Dict, Any

from nlp_parser import parse_user_message
from iata_service import postprocess_entities


def asistent(nombre_empresa: str = "Nombre_empresa") -> List[Dict[str, Any]]:
    """
    Inicia el asistente y devuelve una lista con el JSON final por cada mensaje (log),
    para que puedas mostrarlo como tabla/JSON si el tutor lo pide.
    """
    print(f"Hola, bienvenido a {nombre_empresa}. ¿Como te puedo ayudar?")

    logs: List[Dict[str, Any]] = []

    while True:
        user_msg = input("> ").strip()
        if user_msg.lower() == "salir":
            print("¡Listo! Conversación finalizada.")
            return logs

        parsed = parse_user_message(user_msg)
        final_json = postprocess_entities(parsed)

        origen = final_json.get("origen")
        destino = final_json.get("destino")
        fecha = final_json.get("fecha")
        aerolinea = final_json.get("aerolínea")

        print(f"Perfecto, Comienzo la búsqueda de tu viaje a {destino} desde {origen} para el {fecha} con {aerolinea}.")

        print("\nJSON:")
        print(final_json)

        logs.append(final_json)

        print("\nEscribe otra solicitud o 'salir' para terminar.")


if __name__ == "__main__":
    asistent("Nombre_empresa")
