import os
import discord
from dotenv import load_dotenv

load_dotenv()

async def send_discord_message(user_id: int, message: str) -> str:
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not DISCORD_BOT_TOKEN:
        return "Error: Discord bot token not found"

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        try:
            user = await client.fetch_user(user_id)
            embed = discord.Embed(
                description=message,
                color=discord.Color.from_rgb(100, 200, 200)  # Light bluey-green color
            )
            await user.send(embed=embed)
            print(f"Message sent to user {user_id}")
        except discord.errors.NotFound:
            print(f"User {user_id} not found")
        except discord.errors.Forbidden:
            print(f"Cannot send DM to user {user_id}")
        finally:
            await client.close()

    try:
        await client.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        return f"Error: Failed to send message: {str(e)}"
    return f"Message sent to Discord user {user_id}"