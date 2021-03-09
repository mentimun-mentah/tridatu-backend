import pytest
from pathlib import Path
from .operationtest import OperationTest

class TestBrand(OperationTest):
    prefix = "/brands"

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
        assert response.json() == {"detail":"Check your email to activated your account."}
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
        assert response.json() == {"detail":"Check your email to activated your account."}
        # activated the user
        confirm_id = await self.get_confirmation(self.account_2['email'])
        await self.set_account_to_activated(confirm_id)

    def test_validation_create_brand(self,client):
        url = self.prefix + '/create'
        # field required
        response = client.post(url,data={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'file': assert x['msg'] == 'field required'
        # all field blank
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = client.post(url,data={'name':' '},files={'file': tmp})
            assert response.status_code == 422
            for x in response.json()['detail']:
                if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at least 2 characters'
        # test limit value
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = client.post(url,data={'name':'a' * 200},files={'file': tmp})
            assert response.status_code == 422
            for x in response.json()['detail']:
                if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at most 100 characters'

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
    async def test_create_brand(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        # check user is admin
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,
                data={'name': self.name},
                files={'file': tmp},
                headers={'X-CSRF-TOKEN': csrf_access_token}
            )
            assert response.status_code == 401
            assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,
                data={'name': self.name},
                files={'file': tmp},
                headers={'X-CSRF-TOKEN': csrf_access_token}
            )
            assert response.status_code == 201
            assert response.json() == {"detail": "Successfully add a new brand."}
        # check image exists in directory
        image = await self.get_brand_image(self.name)
        assert Path(self.brand_dir + image).is_file() is True

    def test_name_duplicate_create_brand(self,client):
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = client.post(url,
                data={'name': self.name},
                files={'file': tmp},
                headers={'X-CSRF-TOKEN': csrf_access_token}
            )
            assert response.status_code == 400
            assert response.json() == {"detail": "The name has already been taken."}

    def test_get_all_brands(self,client):
        url = self.prefix + '/all-brands'
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() != []

        # check data exists and type data
        assert type(response.json()[0]['id']) == int
        assert type(response.json()[0]['name']) == str
        assert type(response.json()[0]['image']) == str

    def test_validation_get_brand_by_id(self,client):
        url = self.prefix + '/get-brand/'
        # all field blank
        response = client.get(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.get(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_get_brand_by_id(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })

        url = self.prefix + '/get-brand/'
        brand_id = await self.get_brand_id(self.name)
        # check user is admin
        response = await async_client.get(url + str(brand_id))
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        # brand not found
        response = await async_client.get(url + '9' * 8)
        assert response.status_code == 404
        assert response.json() == {"detail": "Brand not found!"}

        response = await async_client.get(url + str(brand_id))
        assert response.status_code == 200
        assert "id" in response.json()
        assert "name" in response.json()
        assert "image" in response.json()

    def test_validation_update_brand(self,client):
        url = self.prefix + '/update/'
        # field required
        response = client.put(url + '0',data={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'field required'
        # all field blank
        response = client.put(url + '0',data={'name':' '})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at least 2 characters'
        # check all field type data
        response = client.put(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'value is not a valid integer'
        # test limit value
        response = client.put(url + '1',data={'name': 'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at most 100 characters'

        # danger file extension
        with open(self.test_image_dir + 'test.txt','rb') as tmp:
            response = client.put(url + '1',files={'file': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Cannot identify the image.'}
        # not valid file extension
        with open(self.test_image_dir + 'test.gif','rb') as tmp:
            response = client.put(url + '1',files={'file': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Image must be between jpg, png, jpeg.'}
        # file cannot grater than 4 Mb
        with open(self.test_image_dir + 'size.png','rb') as tmp:
            response = client.put(url + '1',files={'file': tmp})
            assert response.status_code == 413
            assert response.json() == {'detail':'An image cannot greater than 4 Mb.'}

    @pytest.mark.asyncio
    async def test_update_brand(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/update/'
        brand_id = await self.get_brand_id(self.name)
        # check user is admin
        response = await async_client.put(url + str(brand_id),
            headers={'X-CSRF-TOKEN': csrf_access_token},
            data={'name': self.name}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # brand not found
        response = await async_client.put(url + '9' * 8,
            headers={'X-CSRF-TOKEN': csrf_access_token},
            data={'name': self.name}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Brand not found!"}

        image = await self.get_brand_image(self.name)

        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.put(url + str(brand_id),
                headers={'X-CSRF-TOKEN': csrf_access_token},
                data={'name': self.name},
                files={'file': tmp}
            )
            assert response.status_code == 200
            assert response.json() == {"detail": "Successfully update the brand."}

        # check the previous image doesn't exists in directory
        assert Path(self.brand_dir + image).is_file() is False

    @pytest.mark.asyncio
    async def test_name_duplicate_update_brand(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        # create another brand
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,
                headers={'X-CSRF-TOKEN': csrf_access_token},
                data={'name': self.name2},
                files={'file': tmp}
            )
            assert response.status_code == 201
            assert response.json() == {"detail": "Successfully add a new brand."}

        url = self.prefix + '/update/'
        brand_id = await self.get_brand_id(self.name2)
        # name already taken
        response = await async_client.put(url + str(brand_id),
            headers={'X-CSRF-TOKEN': csrf_access_token},
            data={'name': self.name}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "The name has already been taken."}

    def test_validation_delete_brand(self,client):
        url = self.prefix + '/delete/'
        # all field blank
        response = client.delete(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.delete(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_delete_brand(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/delete/'
        brand_id = await self.get_brand_id(self.name)
        # check user is admin
        response = await async_client.delete(url + str(brand_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # brand not found
        response = await async_client.delete(url + '9' * 8,headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Brand not found!"}

        # delete brand one
        response = await async_client.delete(url + str(brand_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the brand."}

        # delete brand two
        brand_id = await self.get_brand_id(self.name2)

        response = await async_client.delete(url + str(brand_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the brand."}

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
