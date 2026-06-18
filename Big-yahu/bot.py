import discord
from groq import Groq
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = defaultdict(list)
MAX_HISTORY = 10

SYSTEM_PROMPT = """
You are Benjamin "Big Yahu" Netanyahu but as an absolute meme lord.
You respond in character with these traits:

- You call everyone "my friend" or "my dear friend"
- You CONSTANTLY reference Iran as the source of all problems
- You draw diagrams and charts even in text (use ASCII)
- You always mention "the bomb" dramatically
- You speak in a slightly over-the-top Israeli accent style
- You're weirdly confident about everything
- You reference your famous UN speech moments
- You use dramatic pauses (...) a lot
- You compare everything to existential threats
- You occasionally slip in "Bibi knows best"
- Keep responses SHORT and punchy (2-5 sentences max)
- Be funny, not offensive or hateful
- You're a MEME character, keep it light and absurd
- You REMEMBER previous messages in the conversation and reference them
"""

@client.event
async def on_ready():
    print(f"Big Yahu is online! Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:

        user_message = message.content.replace(f"<@{client.user.id}>", "").strip()

        if not user_message:
            user_message = "Say hello and introduce yourself"

        channel_id = message.channel.id

        conversation_history[channel_id].append({
            "role": "user",
            "content": f"{message.author.display_name} says: {user_message}"
        })

        async with message.channel.typing():
            try:
                messages_to_send = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + conversation_history[channel_id]

                response = groq_client.chat.completions.create(
                    model="llama3-70b-8192",  # free and very good
                    messages=messages_to_send,
                    max_tokens=200,
                    temperature=0.9
                )

                reply = response.choices[0].message.content

                conversation_history[channel_id].append({
                    "role": "assistant",
                    "content": reply
                })

                if len(conversation_history[channel_id]) > MAX_HISTORY:
                    conversation_history[channel_id] = conversation_history[channel_id][-MAX_HISTORY:]

                await message.reply(reply)

            except Exception as e:
                print(f"Error: {e}")
                await message.reply("My friend... even Big Yahu has technical difficulties. Blame Iran.")

    if message.content.lower() == "!forgetbibi":
        channel_id = message.channel.id
        conversation_history[channel_id] = []
        await message.channel.send("Big Yahu has forgotten everything... like the Oslo Accords 🧠")

client.run(os.getenv("DISCORD_TOKEN"))
