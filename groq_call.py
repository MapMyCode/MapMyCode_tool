import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def run_groq_api(prompt, model="openai/gpt-oss-120b"):

    client = Groq(
        api_key=os.environ.get("GROQ_API"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":"You are a helpful AI assistant who is tasked with answering user queries accurately. You must follow the instructions faithfully and do not hallucinate or perform tasks which are not asked."
            }
            ,
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )

    response = chat_completion.choices[0].message.content
    return response