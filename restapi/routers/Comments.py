from fastapi import APIRouter, Depends, HTTPException
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

    user = await UserFetch.filter_by_id(authorize.get_jwt_subject())

    if user['role'] == 'admin':
        raise HTTPException(status_code=403,detail="Admin cannot create comments in their own product.")

    if comment.comment_type == 'product' and not await ProductFetch.filter_by_id(comment.comment_id):
        raise HTTPException(status_code=404,detail="Product not found!")

    if message_cooldown.cooldown_message_sending(comment.comment_type, comment.comment_id, user['id']) is True:
        raise HTTPException(
            status_code=403,
            detail="You've already added comment a moment ago. Please try again later."
        )

    await CommentCrud.create_comment(**comment.dict(),user_id=user['id'])
    return {"detail": "Comment successfully added."}

@router.get('/all-comments',response_model=CommentPaginate)
async def get_all_comments(query_string: get_all_query_comment = Depends()):
    return await CommentFetch.get_all_comments_paginate(**query_string)
