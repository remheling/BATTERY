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

# ==================================================
# 🛡 GUARD — удаление запрещённых команд
# ==================================================
async def guard_commands(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    if not message.text:
        return

    text = message.text.lower()

    if not any(text.startswith(cmd) for cmd in FORBIDDEN_COMMANDS):
        return

    # OWNER и админы могут писать команды
    if is_admin(message.from_user.id):
        return

    # удаляем сообщение и предупреждаем
    try:
        await message.delete()
        await message.answer(WARNING_TEXT)
    except Exception:
        return

    # регистрируем нарушение
    level = register_violation(message.from_user.id)

    # первое нарушение — без мута
    if level < 2:
        return

    mute_seconds = get_mute_time(level)
    until = int(time.time() + mute_seconds)

    try:
        await message.chat.restrict(
            user_id=message.from_user.id,
            permissions={},
            until_date=until
        )
    except Exception:
        return

    mute_user(message.from_user.id, until)


# ==================================================
# ➕ ADD ADMIN (OWNER ONLY, ответом)
# ==================================================
async def add_admin(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await messagemessage := message.answer("Ответь командой на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user
    admins.add(user.id)

    display = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    await message.answer(f"✅ {display} добавлен в админы.")


# ==================================================
# ➖ DEL ADMIN (OWNER ONLY, ответом)
# ==================================================
async def del_admin(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой на сообщение админа.")
        return

    user = message.reply_to_message.from_user
    admins.discard(user.id)

    display = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    await message.answer(f"❌ {display} удалён из админов.")


# ==================================================
# 📊 MUTE STATUS — список замьюченных
# ==================================================
async def mute_status(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not muted_users:
        await message.answer("🔓 Сейчас никто не в муте.")
        return

    now = time.time()
    text = "🔇 Замьюченные пользователи:\n\n"

    for user_id, until in muted_users.items():
        minutes = max(0, int((until - now) / 60))

        try:
            member = await message.bot.get_chat_member(
                message.chat.id,
                user_id
            )
            user = member.user

            if user.username:
                user_display = f"@{user.username}"
            else:
                user_display = f"{user.first_name} (`{user.id}`)"

        except Exception:
            user_display = f"`{user_id}`"

        text += f"• {user_display} — {minutes} мин.\n"

    await message.answer(text, parse_mode="Markdown")


# ==================================================
# ♻ RESET ALL MUTS (OWNER ONLY)
# ==================================================
async def reset_mute(message: Message):
    if not is_owner(message.from_user.id):
        return

    for user_id in list(muted_users.keys()):
        try:
            await message.chat.restrict(
                user_id=user_id,
                permissions={
                    "can_send_messages": True,
                    "can_send_media_messages": True,
                    "can_send_polls": True,
                    "can_send_other_messages": True
                }
            )
        except Exception:
            pass

        unmute_user(user_id)

    await message.answer("✅ Все муты сброшены.")


# ==================================================
# 🔓 RESET ONE MUTE (OWNER ONLY, ответом)
# ==================================================
async def reset_mute_one(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user

    try:
        await message.chat.restrict(
            user_id=user.id,
            permissions={
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_polls": True,
                "can_send_other_messages": True
            }
        )
    except Exception:
        pass

    unmute_user(user.id)

    display = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    await message.answer(f"🔓 {display} размьючен.")


