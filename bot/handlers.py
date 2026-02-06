import time
from aiogram.types import Message
from aiogram.filters import Command
from bot.config import FORBIDDEN_COMMANDS, WARNING_TEXT
from bot.permissions import is_owner, is_admin
from bot.storage import (
    admins,
    muted_users,
    register_violation,
    get_mute_time,
    mute_user,
    unmute_user
)

# 🛡 GUARD
async def guard_commands(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    if not message.text:
        return

    text = message.text.lower()

    if not any(text.startswith(cmd) for cmd in FORBIDDEN_COMMANDS):
        return

    if is_admin(message.from_user.id):
        return

    await message.delete()
    await message.answer(WARNING_TEXT)

    level = register_violation(message.from_user.id)

    if level < 2:
        return

    mute_seconds = get_mute_time(level)
    until = int(time.time() + mute_seconds)

    await message.chat.restrict(
        user_id=message.from_user.id,
        permissions={},
        until_date=until
    )

    mute_user(message.from_user.id, until)


# ➕ ADD ADMIN (OWNER ONLY)
async def add_admin(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответь на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user
    admins.add(user.id)

    await message.answer(f"✅ @{user.username or user.first_name} добавлен в админы.")


# ➖ DEL ADMIN (OWNER ONLY)
async def del_admin(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответь на сообщение админа.")
        return

    user = message.reply_to_message.from_user
    admins.discard(user.id)

    await message.answer(f"❌ @{user.username or user.first_name} удалён из админов.")


# 📊 MUTE STATUS
async def mute_status(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not muted_users:
        await message.answer("🔓 Сейчас никто не в муте.")
        return

    text = "🔇 Замьюченные пользователи:\n\n"
    now = time.time()

    for user_id, until in muted_users.items():
        mins = int((until - now) / 60)
        text += f"• ID `{user_id}` — {mins} мин.\n"

    await message.answer(text, parse_mode="Markdown")


# ♻ RESET ALL
async def reset_mute(message: Message):
    if not is_owner(message.from_user.id):
        return

    for user_id in list(muted_users.keys()):
        await message.chat.restrict(
            user_id=user_id,
            permissions={
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_polls": True,
                "can_send_other_messages": True
            }
        )
        unmute_user(user_id)

    await message.answer("✅ Все муты сброшены.")


# 🔓 RESET ONE
async def reset_mute_one(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответь на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user

    await message.chat.restrict(
        user_id=user.id,
        permissions={
            "can_send_messages": True,
            "can_send_media_messages": True,
            "can_send_polls": True,
            "can_send_other_messages": True
        }
    )

    unmute_user(user.id)
    await message.answer(f"🔓 @{user.username or user.first_name} размьючен.")
