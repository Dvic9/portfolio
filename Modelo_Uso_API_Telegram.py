import requests
import os


#Constantes Configuração
TELEGRAM_BOT_TOKEN = "Meu-Token"
TELEGRAM_CHAT_ID = "Meu_ID" 
TELEGRAM_ENDPOINT = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def enviar_notificacao_telegram(texto_mensagem: str):

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto_mensagem,
        "parse_mode": "Markdown", # Permite usar *negrito* e `código`
    }

    #Tentando enviar mensagem
    
    try:
        #Requisição http
        response = requests.post(TELEGRAM_ENDPOINT, data=payload)
        
        # Se o status for de sucesso (200) E o json indicar ok, ele retorna como sucessoo
        if response.status_code == 200 and response.json().get("ok"):
            print("\n✅ SUCESSO! A mensagem foi enviada ao Telegram.")
            print("Resposta da API:")
            return {"success": True, "response": response.json()}
        else:
            #Caso contrário, ele retorna erro e mostra os detalhes pra ver o que ou onde falhou
            print(f"\n❌ FALHA ao enviar. Status: {response.status_code}")
            print(f"Detalhes do Erro: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO DE CONEXÃO CRÍTICO: {e}")
        return {"success": False, "error": str(e)}



# Testes

# Dados fictícos
CLIENTE_NOME = "Cliente Teste Ranny Rosa"
VALOR_TOTAL = 459.90
FORMA_PAGAMENTO = "Cartão de Crédito"


# Estrutura da mensagem
mensagem_teste = (
    "🔔 *NOVO PEDIDO DE TESTE RECEBIDO!* 🔔\n\n"
    f"👤 Cliente: `{CLIENTE_NOME}`\n"
    f"💸 Valor Total: *R$ {VALOR_TOTAL:.2f}*\n"
    f"💳 Forma de Pagamento: {FORMA_PAGAMENTO}\n\n"
    "Esta é uma notificação de teste isolada."
)

# Execução da função
resultado = enviar_notificacao_telegram(mensagem_teste)
#printando o resultado
print("\nResultado da função:", resultado)