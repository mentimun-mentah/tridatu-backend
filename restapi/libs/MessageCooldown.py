from fastapi.requests import Request

class MessageCooldown:
    def __init__(self,request: Request):
        self.redis = request.app.state.redis
        self.seconds = 15

    def cooldown_message_sending(self, message_type: str, message_id: int, user_id: int) -> bool:
        if self.redis.get(f"{message_type}:{message_id}:{user_id}") is None:
            self.redis.set(f"{message_type}:{message_id}:{user_id}","cooldown",self.seconds)
            return False
        return True
