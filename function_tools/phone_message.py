import asyncio
import os
import threading
import pickle
from .discord_message import send_discord_message
from openai import OpenAI
import google.generativeai as genai

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def send_message_to_phone(user_id: str, message: str) -> str:
    try:
        user_id_int = 123
        # user_id_int = int(user_id)
    except ValueError:
        return "Error: Invalid user ID. Must be an integer."

    # Replace escaped newlines with actual newlines
    message = message.replace('\\\\n', '\n').replace('\\n', '\n')
    
    
    # Prepare the system message with the function_response if available
    system_message = "You are a helpful assistant that will take an input message and modify it to use Discord's markdown formatting to better suit the theme of a discord message. Make sure to include all the information from the original text. Do not make up information. Include links etc. Reply with ONLY the message content."
        
    print(system_message)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
    )
    
    message = response.choices[0].message.content
    
    # Use Gemini api instead
    
    # model = genai.GenerativeModel(
    #     model_name="gemini-1.5-flash-exp-0827",
    #     system_instruction=system_message,
    # )
    
    # response = model.generate_content(message)
    # message = response.text
    
    # Create a new event loop for the thread
    new_loop = asyncio.new_event_loop()

    # Define a function to run the send_discord_message in the new loop
    def run_send_discord_message():
        asyncio.set_event_loop(new_loop)
        return new_loop.run_until_complete(send_discord_message(user_id_int, message))

    # Create and start the thread
    thread = threading.Thread(target=run_send_discord_message)
    thread.start()

    # Return immediately without waiting for the thread to complete
    return f"Message sending process started for Discord user {user_id_int}"