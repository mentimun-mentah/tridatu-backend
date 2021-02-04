import pytest
from pathlib import Path
from .operationtest import OperationTest

class TestOutlet(OperationTest):
    prefix = '/outlets'

    @pytest.mark.asyncio
    async def test_add_user(self,async_client):
        url = '/users/register'
        # register user admin
        response = await async_client.post(url,
            json={
                'username': self.account_1['username'],
                'email': self.account_1['email'],
                'password': self.account_1['password'],
                'confirm_password': self.account_1['password']
            }
        )
        assert response.status_code == 201
        assert response.json() == {"detail":"Check your email to activated user."}
        # activated the user admin
        confirm_id = await self.get_confirmation(self.account_1['email'])
        await self.set_account_to_activated(confirm_id)
        await self.set_user_to_admin(self.account_1['email'])

        # register user not admin
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

    def test_validation_create_outlet(self,client):
        url = self.prefix + '/create'
        # image required
        response = client.post(url,files={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'file': assert x['msg'] == 'field required'
        # danger file extension
        with open(self.test_image_dir + 'test.txt','rb') as tmp:
            response = client.post(url,files={'file': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Cannot identify the image.'}
        # not valid file extension
        with open(self.test_image_dir + 'test.gif','rb') as tmp:
            response = client.post(url,files={'file': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Image must be between jpg, png, jpeg.'}
        # file cannot grater than 4 Mb
        with open(self.test_image_dir + 'size.png','rb') as tmp:
            response = client.post(url,files={'file': tmp})
            assert response.status_code == 413
            assert response.json() == {'detail':'An image cannot greater than 4 Mb.'}

    @pytest.mark.asyncio
    async def test_create_outlet(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        # check user is admin
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,files={'file': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 401
            assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,files={'file': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail": "Successfully add a new outlet."}
        # check image exists in directory
        image = await self.get_last_outlet_image()
        assert Path(self.outlet_dir + image).is_file() is True

    def test_get_all_outlets(self,client):
        url = self.prefix + '/all-outlets'
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() != []

        # check data exists and type data
        assert type(response.json()[0]['id']) == int
        assert type(response.json()[0]['image']) == str

    def test_validation_delete_outlet(self,client):
        url = self.prefix + '/delete/'
        # all field blank
        response = client.delete(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'outlet_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.delete(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'outlet_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_delete_outlet(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/delete/'
        outlet_id = await self.get_last_outlet_id()
        # check user is admin
        response = await async_client.delete(url + str(outlet_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # outlet not found
        response = await async_client.delete(url + '9' * 8,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Outlet not found!"}
        # check image already deleted
        image = await self.get_last_outlet_image()

        response = await async_client.delete(url + str(outlet_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the outlet."}

        assert Path(self.outlet_dir + image).is_file() is False
        # check outlet has been deleted
        response = await async_client.delete(url + str(outlet_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Outlet not found!"}

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
