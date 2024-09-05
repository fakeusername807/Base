import asyncio, os, re, random, pytz, requests, json

async def react_msg(client, message):
    emojis = [
        "👍",
        "❤",
        "🔥",
        "🥰",
        "👏",
        "😁",
        "🤔",
        "😱",
        "🎉",
        "🤩",
        "🤡",
        "😍",
        "❤‍🔥",
        "🌚",
        "🤣",
        "⚡",
        "🏆",
        "🤨",
        "😐",
        "😈",
        "🤓",
        "👻",
        "😇",
        "🤝",
        "🤗",
        "🫡",
        "🎅",
        "🎄",
        "🆒",
        "😘",
        "😎",
    ]
    rnd_emoji = random.choice(emojis)
    await client.send_reaction(
        chat_id=message.chat.id, message_id=message.id, emoji=rnd_emoji, big=True
    )
    return
