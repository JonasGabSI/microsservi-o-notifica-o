import requests

# 1. Endereço do nosso Microsserviço
URL_API = "http://127.0.0.1:8001/api/notificacoes/criar/"

API_KEY = "74fb8f2fcbeb69f5"  

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "user_id": 1,
    "titulo": "Disparo Automático",
    "mensagem": "Parabéns! Este aviso foi gerado por um terceiro sistema."
}
try:
    resposta = requests.post(URL_API, json=payload, headers=headers)

    if resposta.status_code in [200, 201]:
        print("\nSUCESSO! O microsserviço respondeu:")
        print(resposta.json())
    else:
        print(f"\nERRO {resposta.status_code}: A API recusou o pacote.")
        print("Motivo:", resposta.text)

except requests.exceptions.ConnectionError:
    print("\nERRO CRÍTICO: Não foi possível encontrar a porta 8001.")
    print("Verifique se o servidor 'python manage.py runserver 8001' está ligado!")