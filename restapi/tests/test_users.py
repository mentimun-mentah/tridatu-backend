import pytest
from config import database
from models.UserModel import users
from models.ConfirmationModel import confirmation
from sqlalchemy.sql import select

class TestUser:
    prefix = "/users"
    account_1 = {'email':'testtesting@gmail.com','username':'testtesting','password':'testtesting'}

    @pytest.mark.asyncio
    async def get_confirmation(self):
        user = await database.fetch_one(query=select([users]).where(users.c.email == self.account_1['email']))
        confirm = await database.fetch_one(query=select([confirmation]).where(confirmation.c.user_id == user['id']))
        return confirm['id']

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
        assert response.status_code == 422
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
        confirm_id = await self.get_confirmation()
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
    async def test_delete_user_from_db(self,client):
        query = users.delete().where(users.c.email == self.account_1['email'])
        await database.execute(query=query)
