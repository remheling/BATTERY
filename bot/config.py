import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔐 ВЛАДЕЛЕЦ БОТА (ТОЛЬКО ОН МОЖЕТ ПИСАТЬ КОМАНДЫ)
OWNER_ID = 111111111  # <-- ЗАМЕНИ НА СВОЙ ID

# запрещённые команды
FORBIDDEN_COMMANDS = [
    "/start",
    "/add_one",
    "/add_channels",
    "/del_one",
    "/del_all",
    "/status",
    "/auto_delete",
    "/add_time"
]

WARNING_TEXT = "Ай ай, кажется, что эти команды могут писать только админы!🥶"
