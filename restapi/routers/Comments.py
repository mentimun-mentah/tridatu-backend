from fastapi import APIRouter, Path, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.UserController import UserFetch
from controllers.ProductController import ProductFetch
from controllers.CommentController import CommentCrud, CommentFetch
from dependencies.CommentDependant import get_all_query_comment
from schemas.comments.CommentSchema import CommentCreate, CommentPaginate
from libs.MessageCooldown import MessageCooldown

router = APIRouter()

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Comment successfully added."}}}
        },
        403: {
            "description": "Admin cannot create comment or Cooldown 15 seconds",
            "content": {"application/json":{"example": {"detail":"string"}}}
        },
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail":"Product not found!"}}}
        },
    }
)
async def create_comment(
    comment: CommentCreate,
    authorize: AuthJWT = Depends(),
    message_cooldown: MessageCooldown = Depends()
):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        if user['role'] == 'admin':
            raise HTTPException(status_code=403,detail="Admin cannot create comments in their own product.")

        if comment.commentable_type == 'product' and not await ProductFetch.filter_by_id(comment.commentable_id):
            raise HTTPException(status_code=404,detail="Product not found!")

        if message_cooldown.cooldown_message_sending(
            message_type=comment.commentable_type,
            message_id=comment.commentable_id,
            user_id=user['id']
        ) is True:
            raise HTTPException(
                status_code=403,
                detail="You've already added comment a moment ago. Please try again later."
            )

        await CommentCrud.create_comment(**comment.dict(),user_id=user['id'])
        return {"detail": "Comment successfully added."}

@router.get('/all-comments',response_model=CommentPaginate)
async def get_all_comments(query_string: get_all_query_comment = Depends()):
    return await CommentFetch.get_all_comments_paginate(**query_string)

@router.delete('/delete/{comment_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Comment successfully deleted."}}}
        },
        400: {
            "description": "Comment not match with user",
            "content": {"application/json":{"example": {"detail":"Comment not match with the current user."}}}
        },
        404: {
            "description": "Comment not found",
            "content": {"application/json":{"example": {"detail":"Comment not found!"}}}
        }
    }
)
async def delete_comment(comment_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        if comment := await CommentFetch.filter_by_id(comment_id):
            if user['id'] != comment['user_id']:
                raise HTTPException(status_code=400,detail="Comment not match with the current user.")

            await CommentCrud.delete_comment(comment['id'])  # delete comment
            return {"detail": "Comment successfully deleted."}
        raise HTTPException(status_code=404,detail="Comment not found!")
