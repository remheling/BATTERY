from collections import defaultdict
import time

# admin whitelist (user_id)
admins = set()

# user_id -> [violations, last_time]
violations = defaultdict(lambda: [0, 0])

# user_id -> mute_until
muted_users = {}

# муты по уровням
MUTE_LEVELS = {
    2: 10 * 60,        # 10 минут
    3: 60 * 60,        # 1 час
    4: 24 * 60 * 60    # 24 часа
}


def register_violation(user_id: int) -> int:
    now = time.time()
    count, last = violations[user_id]

    if now - last > 3600:
        count = 0

    count += 1
    violations[user_id] = [count, now]
    return count


def get_mute_time(level: int) -> int:
    return MUTE_LEVELS.get(level, MUTE_LEVELS[4])


def mute_user(user_id: int, until: int):
    muted_users[user_id] = until


def unmute_user(user_id: int):
    muted_users.pop(user_id, None)
    violations.pop(user_id, None)
