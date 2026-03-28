import ollama
import json
from datetime import datetime

MEMORY_FILE = "memory.json"

# -------------------------
# MEMÓRIA
# -------------------------
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# -------------------------
# FERRAMENTAS
# -------------------------
def get_time():
    return datetime.now().strftime("%H:%M:%S")

# -------------------------
# DECISÃO DE AÇÃO
# -------------------------
def decide_action(user_input):
    prompt = f"""
Você é um classificador de intenções.

Classifique a mensagem do usuário em uma das opções:
- get_time → se o usuário estiver pedindo a hora atual
- chat → qualquer outro caso

Responda somente com JSON válido:
{{"action": "get_time"}} ou {{"action": "chat"}}

Mensagem: "{user_input}"
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )["message"]["content"]

    
    try:
        data = json.loads(response)
        print("sys ", data.get("action", "chat"))
        return data.get("action", "chat")
    except:
        return "chat"

# -------------------------
# LOOP PRINCIPAL
# -------------------------
def chat():
    memory = load_memory()

    while True:
        user_input = input("Você: ")

        if user_input.lower() in ["sair", "exit"]:
            break

        action = decide_action(user_input)

        if action == "get_time":
            response = f"A hora atual é {get_time()}"
            print("IA:", response)
        else:
            messages = memory + [{"role": "user", "content": user_input}]

            # STREAMING AQUI 👇
            stream = ollama.chat(
                model="mistral",
                messages=messages,
                stream=True
            )

            print("IA:", end=" ")

            response = ""
            for chunk in stream:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                response += content

            print()  # quebra de linha

        # salvar memória
        memory.append({"role": "user", "content": user_input})
        memory.append({"role": "assistant", "content": response})
        save_memory(memory)

chat()