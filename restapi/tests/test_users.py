import pytest
from config import database
from models.UserModel import users
from models.ConfirmationModel import confirmation
from sqlalchemy.sql import select

class TestUser:
    prefix = "/users"
    account_1 = {'email':'testtesting@gmail.com','username':'testtesting','password':'testtesting'}

    @pytest.mark.asyncio
    async def get_confirmation(self, email: str):
        user = await database.fetch_one(query=select([users]).where(users.c.email == email))
        confirm = await database.fetch_one(query=select([confirmation]).where(confirmation.c.user_id == user['id']))
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

    def test_validation_register(self,client):
        url = self.prefix + '/register'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'username': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'password': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'username':'','email':'','password':'','confirm_password':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'username': assert x['msg'] == 'ensure this value has at least 3 characters'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at least 6 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at least 6 characters'
        # check all field type data
        response = client.post(url,json={'username':123,'email':123,'password':123,'confirm_password':123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'username': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'password': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'str type expected'
        # check valid email
        response = client.post(url,json={'email':'asdsd@asd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # check password same as confirm_password
        response = client.post(url,json={'password':'asdasd','confirm_password':'asdasdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'Password must match with confirmation.'

    def test_register_new_user(self,client):
        url = self.prefix + '/register'
        # register new user
        response = client.post(url,
            json={
                'username': self.account_1['username'],
                'email': self.account_1['email'],
                'password': self.account_1['password'],
                'confirm_password': self.account_1['password']
            }
        )
        assert response.status_code == 201
        assert response.json() == {"detail":"Check your email to activated user."}
        # email already exists
        response = client.post(url,
            json={
                'username': self.account_1['username'],
                'email': self.account_1['email'],
                'password': self.account_1['password'],
                'confirm_password': self.account_1['password']
            }
        )
        assert response.status_code == 400
        assert response.json() == {"detail":"The email has already been taken."}

    def test_invalid_token_email(self,client):
        url = self.prefix + '/user-confirm'
        # token not found
        response = client.get(url + '/ngawur')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Token not found!'}

    @pytest.mark.asyncio
    async def test_confirm_email(self,async_client):
        url = self.prefix + '/user-confirm'
        confirm_id = await self.get_confirmation(self.account_1['email'])
        # email activated
        response = await async_client.get(url + f"/{confirm_id}")
        assert response.history[0].status_code == 307
        assert response.history[0].cookies.get("access_token_cookie") is not None
        assert response.history[0].cookies.get("csrf_access_token") is not None

        assert response.history[0].cookies.get("refresh_token_cookie") is not None
        assert response.history[0].cookies.get("csrf_refresh_token") is not None

        response = await async_client.get(url + f"/{confirm_id}")
        assert response.history[0].status_code == 307
        assert response.history[0].cookies.get("access_token_cookie") is not None
        assert response.history[0].cookies.get("csrf_access_token") is not None

        assert response.history[0].cookies.get("refresh_token_cookie") is not None
        assert response.history[0].cookies.get("csrf_refresh_token") is not None

    @pytest.mark.asyncio
    async def test_resend_email_already_activated(self,async_client):
        url = self.prefix + '/resend-email'
        # email already activated
        response = await async_client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Your account already activated.'}
        # set email inactivated
        confirm_id = await self.get_confirmation(self.account_1['email'])
        await self.set_account_to_unactivated(confirm_id)

    def test_validation_resend_email_confirm(self,client):
        url = self.prefix + '/resend-email'

        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'field required'
        # check email blank
        response = client.post(url,json={'email':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # invalid format
        response = client.post(url,json={'email':'dwq@ad'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # email not found in db
        response = client.post(url,json={'email':'o1hwefno@gmail.com'})
        assert response.status_code == 404
        assert response.json() == {'detail': 'Email not found.'}

    def test_resend_email_confirm(self,client):
        url = self.prefix + '/resend-email'
        response = client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 200
        assert response.json() == {"detail":"Email confirmation has send."}

    def test_attempt_to_resend_email_back(self,client):
        # try again 5 minute later
        url = self.prefix + '/resend-email'
        response = client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 400
        assert response.json() == {"detail": "You can try 5 minute later."}

    @pytest.mark.asyncio
    async def test_attempt_to_resend_email_after_not_expired(self,async_client):
        url = self.prefix + '/resend-email'
        # reset time expired
        confirm_id = await self.get_confirmation(self.account_1['email'])
        await self.set_account_to_unexpired(confirm_id)

        response = await async_client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 200
        assert response.json() == {"detail":"Email confirmation has send."}

    def test_validation_login_user(self,client):
        url = self.prefix + '/login'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'password': assert x['msg'] == 'field required'
        # email & password blank
        response = client.post(url,json={'email':'','password':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at least 6 characters'
        # invalid email format
        response = client.post(url,json={'email':'asdd@gmasd','password':'asdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # invalid credential
        response = client.post(url,json={'email': self.account_1['email'],'password':'asdasd'})
        assert response.status_code == 422
        assert response.json() == {"detail":"Invalid credential."}

    @pytest.mark.asyncio
    async def test_login_user_email_not_activated(self,async_client):
        url = self.prefix + '/login'

        response = await async_client.post(url,json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        assert response.status_code == 400
        assert response.json() == {"detail":"Please check your email to activate your account."}
        # set account to activated
        confirm_id = await self.get_confirmation(self.account_1['email'])
        await self.set_account_to_activated(confirm_id)

    def test_login_user(self,client):
        url = self.prefix + '/login'

        response = client.post(url,json={'email': self.account_1['email'], 'password': self.account_1['password']})
        assert response.status_code == 200
        assert response.json() == {"detail":"Successfully login."}
        # check cookies exists
        assert response.cookies.get('access_token_cookie') is not None
        assert response.cookies.get('csrf_access_token') is not None

        assert response.cookies.get('refresh_token_cookie') is not None
        assert response.cookies.get('csrf_refresh_token') is not None

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,client):
        query = users.delete().where(users.c.email == self.account_1['email'])
        await database.execute(query=query)
