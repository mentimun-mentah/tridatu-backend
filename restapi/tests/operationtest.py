import pytest, bcrypt, json, os
from config import database
from sqlalchemy import desc
from sqlalchemy.sql import select, func
from models.UserModel import user
from models.ConfirmationModel import confirmation
from models.PasswordResetModel import password_reset
from models.AddressModel import address
from models.OutletModel import outlet
from models.BrandModel import brand
from models.CategoryModel import category
from models.SubCategoryModel import sub_category
from models.ItemSubCategoryModel import item_sub_category
from models.ProductModel import product
from models.CommentModel import comment
from models.ReplyModel import reply
from models.VariantModel import variant
from models.CartModel import cart
from models.WishlistModel import wishlist
from models.PromoModel import promo

class OperationTest:
    name = 'testtesttttttt'
    name2 = 'testtesttttttt2'
    account_1 = {'email':'testtesting@gmail.com','username':'testtesting','password':'testtesting'}
    account_2 = {'email':'testtesting2@gmail.com','username':'testtesting2','password':'testtesting2'}
    base_dir = os.path.join(os.path.dirname(__file__),'../static/')
    test_image_dir = base_dir + 'test_image/'
    avatar_dir = base_dir + 'avatars/'
    outlet_dir = base_dir + 'outlets/'
    brand_dir = base_dir + 'brands/'
    product_dir = base_dir + 'products/'
    promo_dir = base_dir + 'promos/'

    # ================ USER SECTION ================

    @pytest.mark.asyncio
    async def get_user_avatar(self,email: str):
        user_data = await database.fetch_one(query=select([user]).where(user.c.email == email))
        return user_data['avatar']

    @pytest.mark.asyncio
    async def set_user_to_admin(self,email: str):
        query = user.update().where(user.c.email == email)
        await database.execute(query=query,values={'role': 'admin'})

    @pytest.mark.asyncio
    async def set_user_to_guest(self,email: str):
        query = user.update().where(user.c.email == email)
        await database.execute(query=query,values={'role':'guest'})

    @pytest.mark.asyncio
    async def reset_password_user_to_default(self,email: str):
        query = user.update().where(user.c.email == email)
        password = self.account_1['password'] if email == self.account_1['email'] else self.account_2['password']
        hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        await database.execute(query=query,values={"password": hashed_pass.decode('utf-8')})

    @pytest.mark.asyncio
    async def delete_password_user(self,email: str):
        query = user.update().where(user.c.email == email)
        await database.execute(query=query,values={"password": None})

    @pytest.mark.asyncio
    async def add_password_user(self,email: str, password: str):
        query = user.update().where(user.c.email == email)
        hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        await database.execute(query=query,values={"password": hashed_pass.decode('utf-8')})

    @pytest.mark.asyncio
    async def get_confirmation(self, email: str):
        user_data = await database.fetch_one(query=select([user]).where(user.c.email == email))
        confirm = await database.fetch_one(query=select([confirmation]).where(confirmation.c.user_id == user_data['id']))
        return confirm['id']

    @pytest.mark.asyncio
    async def set_account_to_activated(self, id_: str):
        query = confirmation.update().where(confirmation.c.id == id_)
        await database.execute(query=query,values={"activated": True})

    @pytest.mark.asyncio
    async def set_account_to_unactivated(self, id_: str):
        query = confirmation.update().where(confirmation.c.id == id_)
        await database.execute(query=query,values={"activated": False})

    @pytest.mark.asyncio
    async def set_account_to_unexpired(self, id_: str):
        confirm = await database.fetch_one(query=select([confirmation]).where(confirmation.c.id == id_))
        query = confirmation.update().where(confirmation.c.id == id_)
        await database.execute(query=query,values={"resend_expired": confirm['resend_expired'] - 300})  # decrease 5 minute

    @pytest.mark.asyncio
    async def decrease_password_reset(self, email: str):
        reset = await database.fetch_one(query=select([password_reset]).where(password_reset.c.email == email))
        query = password_reset.update().where(password_reset.c.email == email)
        await database.execute(query=query,values={"resend_expired": reset['resend_expired'] - 300})  # decrease 5 minute

    @pytest.mark.asyncio
    async def get_password_reset(self, email: str):
        reset = await database.fetch_one(query=select([password_reset]).where(password_reset.c.email == email))
        return reset['id']

    @pytest.mark.asyncio
    async def get_user_id(self, email: str):
        user_data = await database.fetch_one(query=select([user]).where(user.c.email == email))
        return user_data['id']

    @pytest.mark.asyncio
    async def delete_user_from_db(self):
        # delete user 1
        query = user.delete().where(user.c.email == self.account_1['email'])
        await database.execute(query=query)
        # delete user 2
        query = user.delete().where(user.c.email == self.account_2['email'])
        await database.execute(query=query)

    # ================ ADDRESS SECTION ================

    @pytest.mark.asyncio
    async def get_address_id(self,user_id: int):
        add = await database.fetch_one(query=select([address]).where(address.c.user_id == user_id))
        return add['id']

    # ================ OUTLET SECTION ================

    @pytest.mark.asyncio
    async def get_last_outlet_image(self):
        query = select([outlet]).order_by(desc(outlet.c.id)).limit(1)
        outlet_data = await database.fetch_one(query=query)
        return outlet_data['image']

    @pytest.mark.asyncio
    async def get_last_outlet_id(self):
        query = select([outlet]).order_by(desc(outlet.c.id)).limit(1)
        outlet_data = await database.fetch_one(query=query)
        return outlet_data['id']

    # ================ BRAND SECTION ================

    @pytest.mark.asyncio
    async def get_brand_image(self,name: str):
        query = select([brand]).where(brand.c.name == name)
        brand_data = await database.fetch_one(query=query)
        return brand_data['image']

    @pytest.mark.asyncio
    async def get_brand_id(self,name: str):
        query = select([brand]).where(brand.c.name == name)
        brand_data = await database.fetch_one(query=query)
        return brand_data['id']

    # ================ CATEGORY SECTION ================

    @pytest.mark.asyncio
    async def get_category_id(self,name: str):
        query = select([category]).where(category.c.name == name)
        category_data = await database.fetch_one(query=query)
        return category_data['id']

    # ================ SUB-CATEGORY SECTION ================

    @pytest.mark.asyncio
    async def get_sub_category_id(self,name: str):
        query = select([sub_category]).where(sub_category.c.name == name)
        sub_category_data = await database.fetch_one(query=query)
        return sub_category_data['id']

    # ================ ITEM-SUB-CATEGORY SECTION ================

    @pytest.mark.asyncio
    async def get_item_sub_category_id(self,name: str):
        query = select([item_sub_category]).where(item_sub_category.c.name == name)
        item_sub_category_data = await database.fetch_one(query=query)
        return item_sub_category_data['id']

    # ================ PRODUCT SECTION ================

    @pytest.mark.asyncio
    async def get_product_id(self,name: str):
        query = select([product]).where(product.c.name == name)
        product_data = await database.fetch_one(query=query)
        return product_data['id']

    @pytest.mark.asyncio
    async def get_product_image(self,name: str):
        query = select([product.c.image_product]).where(product.c.name == name)
        product_data = await database.fetch_one(query=query)
        return json.loads(product_data['image_product'])

    @pytest.mark.asyncio
    async def update_product_by_name(self,name: str, **kwargs):
        kwargs.update({"updated_at": func.now()})
        await database.execute(query=product.update().where(product.c.name == name),values=kwargs)

    # ================ WISHLIST SECTION ================

    @pytest.mark.asyncio
    async def get_len_of_wishlist_user(self,user_id: int):
        query = select([func.count()]).where(wishlist.c.user_id == user_id).select_from(wishlist).as_scalar()
        return await database.execute(query=query)

    # ================ COMMENT SECTION ================

    @pytest.mark.asyncio
    async def get_comment_id(self, message: str, commentable_id: int, commentable_type: str):
        query = select([comment]).where(
            (comment.c.message == message) &
            (comment.c.commentable_id == commentable_id) &
            (comment.c.commentable_type == commentable_type)
        )
        comment_data = await database.fetch_one(query=query)
        return comment_data['id']

    # ================ REPLY SECTION ================

    @pytest.mark.asyncio
    async def get_reply_id(self, message: str, comment_id: int):
        query = select([reply]).where((reply.c.message == message) & (reply.c.comment_id == comment_id))
        reply_data = await database.fetch_one(query=query)
        return reply_data['id']

    # ================ VARIANT SECTION ================

    @pytest.mark.asyncio
    async def get_all_variant_by_product_id(self, product_id: int):
        query = select([variant]).where(variant.c.product_id == product_id)
        variant_data = await database.fetch_all(query=query)
        return [{key:value for key,value in data.items()} for data in variant_data]

    @pytest.mark.asyncio
    async def change_variant_stock_zero(self, id_: int):
        query = variant.update().where(variant.c.id == id_)
        await database.execute(query=query,values={'stock': 0})

    # ================ CART SECTION ================

    @pytest.mark.asyncio
    async def get_qty_cart(self, variant_id: int, user_id: int):
        query  = select([cart]).where((cart.c.variant_id == variant_id) & (cart.c.user_id == user_id))
        cart_data = await database.fetch_one(query=query)
        return cart_data['qty']

    @pytest.mark.asyncio
    async def get_all_cart_by_user_id(self, user_id: int):
        cart_data = await database.fetch_all(query=select([cart]).where(cart.c.user_id == user_id))
        return [{key:value for key,value in data.items()} for data in cart_data]

    # ================ PROMO SECTION ================

    @pytest.mark.asyncio
    async def get_promo_image(self,name: str):
        query = select([promo]).where(promo.c.name == name)
        promo_data = await database.fetch_one(query=query)
        return promo_data['image']

    @pytest.mark.asyncio
    async def get_promo_id(self,name: str):
        query = select([promo]).where(promo.c.name == name)
        promo_data = await database.fetch_one(query=query)
        return promo_data['id']

    @pytest.mark.asyncio
    async def update_promo_by_name(self,name: str, **kwargs):
        await database.execute(query=promo.update().where(promo.c.name == name),values=kwargs)
