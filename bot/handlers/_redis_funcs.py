import os

import redis.asyncio as redis

redis_host = os.getenv("MY_REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, decode_responses=True)


# TODO: add type annotations
async def save_msg_data_to_redis(msg_name, msg):
    print(f"saved {msg.text}")
    user_id = msg.chat.id
    msg_data = {"chat_id": msg.chat.id, "message_id": msg.message_id, "text": msg.text}

    await r.hset(f"saved_messages:{msg_name}:{user_id}", mapping=msg_data)


async def get_msg_data_from_redis(msg_name, user_id):
    msg = await r.hgetall(f"saved_messages:{msg_name}:{user_id}")
    print("get", msg)
    return msg
