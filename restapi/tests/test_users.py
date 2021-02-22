import pytest
from app import app
from pathlib import Path
from .operationtest import OperationTest

class TestUser(OperationTest):
    prefix = "/users"

    @pytest.mark.asyncio
    async def test_add_another_user(self,async_client):
        url = self.prefix + '/register'
        # register another user
        response = await async_client.post(url,
            json={
                'username': self.account_2['username'],
                'email': self.account_2['email'],
                'password': self.account_2['password'],
                'confirm_password': self.account_2['password']
            }
        )
        assert response.status_code == 201
        assert response.json() == {"detail":"Check your email to activated user."}
        # activated the user
        confirm_id = await self.get_confirmation(self.account_2['email'])
        await self.set_account_to_activated(confirm_id)

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
        # test limit value
        response = client.post(url,json={
            'username':'a' * 200,
            'email':'a' * 200 + '@example.com',
            'password':'a' * 200,
            'confirm_password':'a' * 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'username': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at most 100 characters'
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
            if x['loc'][-1] == 'password': assert x['msg'] == 'password must match with password confirmation'

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
        # set email unactivated
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
        # test limit value
        response = client.post(url,json={'email': 'a' * 200 + '@example.com'})
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
        # test limit value
        response = client.post(url,json={'email': 'a' * 200 + '@example.com', 'password': 'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.post(url,json={'email':123,'password':123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'password': assert x['msg'] == 'str type expected'
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

    def test_validation_fresh_token(self,client):
        url = self.prefix + '/fresh-token'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'password':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at least 6 characters'
        # test limit value
        response = client.post(url,json={'password':'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all type data
        response = client.post(url,json={'password': 123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'str type expected'
        # user login
        response = client.post(self.prefix + '/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # password not same as database
        response = client.post(url,headers={'X-CSRF-TOKEN': csrf_access_token},json={'password': 'asdasd'})
        assert response.status_code == 422
        assert response.json() == {"detail":"Password does not match with our records."}

    def test_fresh_token(self,client):
        # user login
        response = client.post(self.prefix + '/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        access_token_cookie = response.cookies.get('access_token_cookie')
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/fresh-token'

        response = client.post(url,
            headers={'X-CSRF-TOKEN': csrf_access_token},
            json={'password': self.account_1['password']}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully make a fresh token."}
        # access token not same anymore
        assert access_token_cookie != response.cookies.get('access_token_cookie')
        assert csrf_access_token != response.cookies.get('csrf_access_token')

    def test_refresh_token(self,client):
        url = self.prefix + '/login'
        # login to get token from cookie
        response = client.post(url,json={'email': self.account_1['email'], 'password': self.account_1['password']})
        # set cookie to variable
        access_token_cookie = response.cookies.get('access_token_cookie')
        csrf_access_token = response.cookies.get('csrf_access_token')
        csrf_refresh_token = response.cookies.get('csrf_refresh_token')

        # refresh the token
        url = self.prefix + '/refresh-token'
        response = client.post(url,headers={"X-CSRF-TOKEN": csrf_refresh_token})
        assert response.status_code == 200
        assert response.json() == {'detail': 'The token has been refreshed.'}

        # check access cookie not same again
        assert access_token_cookie != response.cookies.get('access_token_cookie')
        assert csrf_access_token != response.cookies.get('csrf_access_token')

    def test_revoke_access_token(self,client,authorize):
        # login to get token from cookie
        url = self.prefix + '/login'
        response = client.post(url,json={'email': self.account_1['email'], 'password': self.account_1['password']})
        # set token and csrf to variable
        access_token_cookie = response.cookies.get('access_token_cookie')
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/access-revoke'
        response = client.delete(url,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {'detail': 'An access token has revoked.'}
        # check token has been revoked
        response = client.delete(url,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Token has been revoked"}
        # check jti store in redis
        jti = authorize.get_raw_jwt(access_token_cookie)['jti']
        assert app.state.redis.get(jti) == "true"

    def test_revoke_refresh_token(self,client,authorize):
        # login to get token from cookie
        url = self.prefix + '/login'
        response = client.post(url,json={'email': self.account_1['email'], 'password': self.account_1['password']})
        # set token and csrf to variable
        refresh_token_cookie = response.cookies.get('refresh_token_cookie')
        csrf_refresh_token = response.cookies.get('csrf_refresh_token')

        url = self.prefix + '/refresh-revoke'
        response = client.delete(url,headers={"X-CSRF-TOKEN": csrf_refresh_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "An refresh token has revoked."}
        # check token has been revoked
        response = client.delete(url,headers={"X-CSRF-TOKEN": csrf_refresh_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Token has been revoked"}
        # check jti store in redis
        jti = authorize.get_raw_jwt(refresh_token_cookie)['jti']
        assert app.state.redis.get(jti) == "true"

    def test_delete_all_cookies(self,client):
        url = self.prefix + '/login'

        response = client.post(url,json={'email': self.account_1['email'], 'password': self.account_1['password']})
        assert response.status_code == 200
        assert response.json() == {"detail":"Successfully login."}
        # check cookies exists
        assert response.cookies.get('access_token_cookie') is not None
        assert response.cookies.get('csrf_access_token') is not None

        assert response.cookies.get('refresh_token_cookie') is not None
        assert response.cookies.get('csrf_refresh_token') is not None

        url = self.prefix + '/delete-cookies'

        response = client.delete(url)
        assert response.status_code == 200
        assert response.json() == {"detail":"All cookies have been deleted."}
        # check cookies doesn't exists
        assert response.cookies.get('access_token_cookie') is None
        assert response.cookies.get('csrf_access_token') is None

        assert response.cookies.get('refresh_token_cookie') is None
        assert response.cookies.get('csrf_refresh_token') is None

    def test_validation_send_email_reset_password(self,client):
        url = self.prefix + '/password-reset/send'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'field required'
        # email blank
        response = client.post(url,json={'email': ''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # test limit value
        response = client.post(url,json={'email': 'a' * 200 + '@example.com'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # invalid format email
        response = client.post(url,json={'email': 'asdd@gmasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # email not found in database
        response = client.post(url,json={'email': 'ngasalbgtasddd@gmail.com'})
        assert response.status_code == 404
        assert response.json() == {"detail":"We can't find a user with that e-mail address."}

    @pytest.mark.asyncio
    async def test_send_email_reset_password_user_not_activated(self,async_client):
        # set user not activated
        confirm_id = await self.get_confirmation(self.account_1['email'])
        await self.set_account_to_unactivated(confirm_id)

        url = self.prefix + '/password-reset/send'
        response = await async_client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 400
        assert response.json() == {"detail": "Please activate your account first."}
        # set user to activated
        await self.set_account_to_activated(confirm_id)

    @pytest.mark.asyncio
    async def test_send_email_reset_password(self,async_client):
        url = self.prefix + '/password-reset/send'
        # success send email
        response = await async_client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 200
        assert response.json() == {"detail": "We have sent a password reset link to your email."}
        # cooldown 5 minutes
        response = await async_client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 400
        assert response.json() == {"detail": "You can try 5 minute later."}
        # decrease resend_expired 5 minute
        await self.decrease_password_reset(self.account_1['email'])
        # success send email
        response = await async_client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 200
        assert response.json() == {"detail": "We have sent a password reset link to your email."}
        # cooldown 5 minutes again
        response = await async_client.post(url,json={"email": self.account_1['email']})
        assert response.status_code == 400
        assert response.json() == {"detail": "You can try 5 minute later."}

    def test_validation_reset_password(self,client):
        url = self.prefix + '/password-reset/ngawur'
        # field required
        response = client.put(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'password': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'field required'
        # all field blank
        response = client.put(url,json={'email':'','password':'','confirm_password':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at least 6 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at least 6 characters'
        # test limit value
        response = client.put(url,json={
            'email': 'a' * 200 + '@example.com',
            'password': 'a' * 200,
            'confirm_password': 'a' * 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.put(url,json={'email':123,'password':123,'confirm_password':123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
            if x['loc'][-1] == 'password': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'str type expected'
        # check valid format email
        response = client.put(url,json={'email':'asdsd@asd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'email': assert x['msg'] == 'value is not a valid email address'
        # password and confirm not same
        response = client.put(url,json={'password':'asdasd','confirm_password':'asdasdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'password must match with password confirmation'
        # email not found in database
        response = client.put(url,json={'email': 'ngawrubeta@example.com','password':'asdasd','confirm_password':'asdasd'})
        assert response.status_code == 404
        assert response.json() == {"detail":"We can't find a user with that e-mail address."}

    def test_token_not_found_reset_password(self,client):
        url = self.prefix + '/password-reset/ngawur'

        response = client.put(url,json={'email': self.account_2['email'],'password':'asdasd','confirm_password':'asdasd'})
        assert response.status_code == 404
        assert response.json() == {"detail": "Token not found!"}

    @pytest.mark.asyncio
    async def test_email_not_match_with_reset_password(self,async_client):
        reset_id = await self.get_password_reset(self.account_1['email'])
        url = self.prefix + f'/password-reset/{reset_id}'

        response = await async_client.put(url,json={
            'email': self.account_2['email'],
            'password':'asdasd',
            'confirm_password':'asdasd'
        })
        assert response.status_code == 400
        assert response.json() == {"detail":"The password reset token is invalid."}

    @pytest.mark.asyncio
    async def test_reset_password(self,async_client):
        reset_id = await self.get_password_reset(self.account_1['email'])
        url = self.prefix + f'/password-reset/{reset_id}'

        response = await async_client.put(url,json={
            'email': self.account_1['email'],
            'password':'asdasd',
            'confirm_password':'asdasd'
        })
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully reset your password."}

        # check token has been deleted in db
        response = await async_client.put(url,json={
            'email': self.account_1['email'],
            'password':'asdasd',
            'confirm_password':'asdasd'
        })
        assert response.status_code == 404
        assert response.json() == {"detail": "Token not found!"}

    def test_validation_add_password(self,client):
        url = self.prefix + '/add-password'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'password':'','confirm_password':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at least 6 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at least 6 characters'
        # test limit value
        response = client.post(url,json={'password':'a' * 200,'confirm_password':'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.post(url,json={'password':123,'confirm_password':123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'str type expected'
        # check password same as confirm_password
        response = client.post(url,json={'password':'asdasd','confirm_password':'asdasdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'password must match with password confirmation'
        # user login
        response = client.post(self.prefix + '/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # account already has a password
        response = client.post(url,
            headers={"X-CSRF-TOKEN": csrf_access_token},
            json={'password':'asdasd','confirm_password':'asdasd'}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Your account already has a password."}

    @pytest.mark.asyncio
    async def test_add_password(self,async_client):
        # user login
        response = await async_client.post(self.prefix + '/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # delete password user from db
        await self.delete_password_user(self.account_2['email'])

        url = self.prefix + '/add-password'
        response = await async_client.post(url,
            headers={"X-CSRF-TOKEN": csrf_access_token},
            json={'password': self.account_2['password'],'confirm_password': self.account_2['password']}
        )
        assert response.status_code == 201
        assert response.json() == {"detail": "Success add a password to your account."}

    def test_validation_update_password(self,client):
        url = self.prefix + '/update-password'
        # field required
        response = client.put(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'old_password': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'password': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'field required'
        # all field blank
        response = client.put(url,json={'old_password':'','password':'','confirm_password':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'old_password': assert x['msg'] == 'ensure this value has at least 6 characters'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at least 6 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at least 6 characters'
        # test limit value
        response = client.put(url,json={
            'old_password': 'a' * 200,
            'password': 'a' * 200,
            'confirm_password': 'a' * 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'old_password': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'password': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.put(url,json={'old_password':123,'password':123,'confirm_password':123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'old_password': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'password': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'confirm_password': assert x['msg'] == 'str type expected'
        # check password same as confirm_password
        response = client.put(url,json={'password':'asdasd','confirm_password':'asdasdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'password': assert x['msg'] == 'password must match with password confirmation'
        # user login
        response = client.post(self.prefix + '/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # old password not same as database
        response = client.put(url,
            headers={"X-CSRF-TOKEN": csrf_access_token},
            json={
                'old_password': 'asdasd',
                'password': self.account_2['password'],
                'confirm_password': self.account_2['password']
            }
        )
        assert response.status_code == 422
        assert response.json() == {"detail": "Password does not match with our records."}

    @pytest.mark.asyncio
    async def test_update_password_not_exists_in_db(self,async_client):
        url = self.prefix + '/update-password'
        # user login
        response = await async_client.post(self.prefix + '/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # delete password
        await self.delete_password_user(self.account_2['email'])

        response = await async_client.put(url,
            headers={"X-CSRF-TOKEN": csrf_access_token},
            json={'old_password': 'asdasd','password':'asdasd','confirm_password':'asdasd'}
        )
        assert response.status_code == 400
        assert response.json() == {"detail":"Please add your password first."}
        # add password again
        await self.add_password_user(self.account_2['email'],self.account_2['password'])

    def test_update_password(self,client):
        url = self.prefix + '/update-password'
        # user login
        response = client.post(self.prefix + '/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = client.put(url,
            headers={"X-CSRF-TOKEN": csrf_access_token},
            json={'old_password': self.account_2['password'],'password':'asdasd','confirm_password':'asdasd'}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Success update your password."}

    def test_validation_update_avatar(self,client):
        url = self.prefix + '/update-avatar'
        # image required
        response = client.put(url,files={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'file': assert x['msg'] == 'field required'
        # danger file extension
        with open(self.test_image_dir + 'test.txt','rb') as tmp:
            response = client.put(url,files={'file': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Cannot identify the image.'}
        # not valid file extension
        with open(self.test_image_dir + 'test.gif','rb') as tmp:
            response = client.put(url,files={'file': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Image must be between jpg, png, jpeg.'}
        # file cannot grater than 4 Mb
        with open(self.test_image_dir + 'size.png','rb') as tmp:
            response = client.put(url,files={'file': tmp})
            assert response.status_code == 413
            assert response.json() == {'detail':'An image cannot greater than 4 Mb.'}

    @pytest.mark.asyncio
    async def test_update_avatar(self,async_client):
        await self.reset_password_user_to_default(self.account_1['email'])
        await self.reset_password_user_to_default(self.account_2['email'])
        # user login
        response = await async_client.post(self.prefix + '/login', json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/update-avatar'
        # update avatar
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.put(url,files={'file': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 200
            assert response.json() == {"detail": "The image profile has updated."}
        # check file avatar exists in directory
        avatar = await self.get_user_avatar(self.account_1['email'])
        assert Path(self.avatar_dir + avatar).is_file() is True
        # update avatar again
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.put(url,files={'file': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 200
            assert response.json() == {"detail": "The image profile has updated."}
        # check the old one has been deleted
        assert Path(self.avatar_dir + avatar).is_file() is False
        # check file avatar exists in directory
        avatar = await self.get_user_avatar(self.account_1['email'])
        assert Path(self.avatar_dir + avatar).is_file() is True
        # detele avatar in directory
        Path(self.avatar_dir + avatar).unlink()

    def test_validation_update_account(self,client):
        url = self.prefix + '/update-account'
        # field required
        response = client.put(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'username': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'gender': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'field required'
        # all field blank
        response = client.put(url,json={'username':'','gender':'','phone':''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'username':
                assert x['msg'] == 'ensure this value has at least 3 characters'
            if x['loc'][-1] == 'gender':
                assert x['msg'] == "unexpected value; permitted: 'Laki-laki', 'Perempuan', 'Lainnya'"
            if x['loc'][-1] == 'phone':
                assert x['msg'] == 'ensure this value has at least 1 characters'
        # test limit value
        response = client.put(url,json={'username':'a' * 200,'gender':'a' * 200,'phone':'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'username':
                assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'gender':
                assert x['msg'] == "unexpected value; permitted: 'Laki-laki', 'Perempuan', 'Lainnya'"
            if x['loc'][-1] == 'phone':
                assert x['msg'] == 'ensure this value has at most 20 characters'
        # check all field type data
        response = client.put(url,json={'username':123,'gender':123,'phone':123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'username':
                assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'gender':
                assert x['msg'] == "unexpected value; permitted: 'Laki-laki', 'Perempuan', 'Lainnya'"
            if x['loc'][-1] == 'phone':
                assert x['msg'] == 'str type expected'
        # invalid option gender
        response = client.put(url,json={'gender':'laki-laki'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'gender':
                assert x['msg'] == "unexpected value; permitted: 'Laki-laki', 'Perempuan', 'Lainnya'"
        # invalid phone number
        response = client.put(url,json={'phone':'asdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "value is not a valid mobile phone number"
        response = client.put(url,json={'phone':'8762732'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "value is not a valid mobile phone number"

    def test_update_account(self,client):
        # user login
        response = client.post(self.prefix + '/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/update-account'

        response = client.put(url,headers={'X-CSRF-TOKEN': csrf_access_token},json={
            'username':'asdasd',
            'phone':'87862253096',
            'gender':'Laki-laki'
        })
        assert response.status_code == 200
        assert response.json() == {"detail": "Success updated your account."}

    def test_update_account_phone_number_already_taken(self,client):
        # user login
        response = client.post(self.prefix + '/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # check phone number already taken
        url = self.prefix + '/update-account'

        response = client.put(url,headers={'X-CSRF-TOKEN': csrf_access_token},json={
            'username':'asdasd',
            'phone':'87862253096',
            'gender':'Laki-laki'
        })
        assert response.status_code == 400
        assert response.json() == {'detail': 'The phone number has already been taken.'}

    def test_my_user(self,client):
        url = self.prefix + '/my-user'

        # user login
        client.post(self.prefix + '/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })

        response = client.get(url)
        assert response.status_code == 200
        assert 'email' in response.json()
        assert 'username' in response.json()
        assert 'password' in response.json()
        assert 'phone' in response.json()
        assert 'gender' in response.json()
        assert 'role' in response.json()
        assert 'avatar' in response.json()

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
