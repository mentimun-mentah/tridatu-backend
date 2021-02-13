from fastapi import APIRouter, Path, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.ReplyController import ReplyCrud, ReplyFetch
from controllers.UserController import UserFetch
from controllers.CommentController import CommentFetch
from schemas.replies.ReplySchema import ReplyCreate, ReplyCommentData
from libs.MessageCooldown import MessageCooldown
from libs.Parser import parse_int_list
from typing import List, Union

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

    user_id = int(authorize.get_jwt_subject())
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

@router.get('/comments/{comment_id}',response_model=Union[List[ReplyCommentData],ReplyCommentData])
async def get_all_replies_in_comment(comment_id: str = Path(...,min_length=1,description="Example 1-2-3")):
    return await ReplyFetch.get_all_replies_in_comment(parse_int_list(comment_id,"-"))

@router.delete('/delete/{reply_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Reply successfully deleted."}}}
        },
        400: {
            "description": "Reply not match with user",
            "content": {"application/json":{"example": {"detail":"Reply not match with the current user."}}}
        },
        404: {
            "description": "Reply not found",
            "content": {"application/json":{"example": {"detail":"Reply not found!"}}}
        }
    }
)
async def delete_reply(reply_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        if reply := await ReplyFetch.filter_by_id(reply_id):
            if user['id'] != reply['user_id']:
                raise HTTPException(status_code=400,detail="Reply not match with the current user.")

            await ReplyCrud.delete_reply(reply['id'])  # delete reply
            return {"detail": "Reply successfully deleted."}
        raise HTTPException(status_code=404,detail="Reply not found!")
