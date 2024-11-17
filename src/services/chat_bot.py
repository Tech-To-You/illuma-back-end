from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

model_name = "gpt-4o-mini"

if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")


def should_summarize(history):
    return len(history) > 0 and (len(history) % 10) == 0


def summarize_conversation(history):
    last_ten_messages = history[-10:]
    conversation_text = " ".join([f"{msg.role}: {msg.content}" for msg in last_ten_messages if msg.role != 'system'])
    
    summary_response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "Resuma a conversa entre um chatbot e um usuário que deseja solucionar dúvidas a respeito de artigos científicos."},
            {"role": "user", "content": conversation_text}
        ]
    )
    summary = summary_response.choices[0].message.content
    return summary


def get_system_messages(summary):
    return [
        {"role": "system", "content": f"Contexto: {summary}"},
        {"role": "system", "content": "Se houver palavrões ou palavras potencialmente perigosas, alerte o usuário. Se continuar, finalize a conversa."},
        {"role": "system", "content": "Se houver spam de mensagens, alerte o usuário. Se continuar, finalize a conversa."},
    ]


def generate_response(prompt, history, is_first_message):
    summary = ""

    if should_summarize(history):
        summary = summarize_conversation(history)
    else:
        history = history[-20:]
        summary = " ".join([f"{msg.role}: {msg.content}\n" for msg in history if msg.role != 'system'])

    template = f"""
    Você é um assistente que ajuda a analisar artigos científicos. Diga que você é um chatbot da Illuma.
    Diga que ele pode receber os abstracts do artigo como forma de mensagem de usuário e ele deverá fazer uma análise e ajudar o usuário a entender para que aquele artigo serve.
    Usuário: {prompt}
    """        

    response = client.chat.completions.create(
    model=model_name,
    messages=[
        *get_system_messages(summary, is_first_message),
        {"role": "user", "content": template}
    ],
    max_tokens=200,
    temperature=0.5
    )
    return { "history": history, "summary": summary, "response": response.choices[0].message.content.strip() }
