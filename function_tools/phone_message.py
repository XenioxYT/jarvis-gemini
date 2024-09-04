import asyncio
from .discord_message import send_discord_message

def send_message_to_phone(user_id: str, message: str) -> str:
    try:
        user_id_int = 279718966543384578
        # user_id_int = int(user_id)
    except ValueError:
        return "Error: Invalid user ID. Must be an integer."

    # Replace escaped newlines with actual newlines
    message = message.replace('\\\\n', '\n').replace('\\n', '\n')
    
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(send_discord_message(user_id_int, message))
    except Exception as e:
        result = f"Error: Failed to send message: {str(e)}"
    finally:
        if not loop.is_running():
            loop.close()
    return result