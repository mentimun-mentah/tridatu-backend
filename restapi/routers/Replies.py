from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.ReplyController import ReplyCrud
from controllers.UserController import UserFetch
from controllers.CommentController import CommentFetch
from schemas.replies.ReplySchema import ReplyCreate
from libs.MessageCooldown import MessageCooldown

router = APIRouter()

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully reply to this comment."}}}
        },
        403: {
            "description": "Send message cooldown 15 seconds",
            "content": {"application/json":{
                "example": {"detail":"You've already added comment a moment ago. Please try again later."}
            }}
        },
        404: {
            "description": "Comment not found",
            "content": {"application/json": {"example": {"detail":"Comment not found!"}}}
        },
    }
)
async def create_reply(
    reply: ReplyCreate,
    authorize: AuthJWT = Depends(),
    message_cooldown: MessageCooldown = Depends()
):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        if not await CommentFetch.filter_by_id(reply.comment_id):
            raise HTTPException(status_code=404,detail="Comment not found!")

        if message_cooldown.cooldown_message_sending(
            message_type="reply",
            message_id=reply.comment_id,
            user_id=user['id']
        ) is True:
            raise HTTPException(
                status_code=403,
                detail="You've already added comment a moment ago. Please try again later."
            )

        await ReplyCrud.create_reply(**reply.dict(),user_id=user['id'])
        return {"detail": "Successfully reply to this comment."}
