from fastapi.requests import Request

class MessageCooldown:
    def __init__(self,request: Request):
        self.redis = request.app.state.redis
        self.seconds = 15

    def cooldown_message_sending(self, comment_type: str, comment_id: int, user_id: int) -> bool:
        if self.redis.get(f"{comment_type}:{comment_id}:{user_id}") is None:
            self.redis.set(f"{comment_type}:{comment_id}:{user_id}","cooldown",self.seconds)
            return False
        return True
