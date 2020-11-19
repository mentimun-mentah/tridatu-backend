import pytest, bcrypt, os
from config import database
from sqlalchemy import desc
from sqlalchemy.sql import select
from models.UserModel import user
from models.ConfirmationModel import confirmation
from models.PasswordResetModel import password_reset
from models.AddressModel import address
from models.OutletModel import outlet
from models.BrandModel import brand

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
        query = select([brand]).where(brand.c.name_brand == name)
        brand_data = await database.fetch_one(query=query)
        return brand_data['image_brand']

    @pytest.mark.asyncio
    async def get_brand_id(self,name: str):
        query = select([brand]).where(brand.c.name_brand == name)
        brand_data = await database.fetch_one(query=query)
        return brand_data['id_brand']
