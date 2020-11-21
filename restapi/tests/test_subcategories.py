import pytest
from .operationtest import OperationTest

class TestSubCategory(OperationTest):
    prefix = "/sub-categories"

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

    def test_create_category(self,client):
        # user admin login
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # create category
        response = client.post('/categories/create',
            json={'name_category': self.name},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new category."}

    def test_validation_create_sub_category(self,client):
        url = self.prefix + '/create'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name_sub_category': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'name_sub_category': '','category_id': 0})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name_sub_category': assert x['msg'] == 'ensure this value has at least 3 characters'
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'ensure this value is greater than 0'
        # test limit value
        response = client.post(url,json={'name_sub_category': 'a' * 200,'category_id': 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name_sub_category': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.post(url,json={'name_sub_category': 123,'category_id': '123'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name_sub_category': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_create_sub_category(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        category_id = await self.get_category_id(self.name)
        # check user is admin
        response = await async_client.post(url,
            json={'name_sub_category': self.name,'category_id': category_id},
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
        # category_id not found
        response = await async_client.post(url,
            json={'name_sub_category': self.name,'category_id': 99999},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Category not found!"}

        response = await async_client.post(url,
            json={'name_sub_category': self.name,'category_id': category_id},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new sub-category."}

    @pytest.mark.asyncio
    async def test_name_duplicate_create_sub_category(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        category_id = await self.get_category_id(self.name)

        response = await async_client.post(url,
            json={'name_sub_category': self.name,'category_id': category_id},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "The name has already been taken."}

    @pytest.mark.asyncio
    async def test_delete_category(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # delete category
        category_id = await self.get_category_id(self.name)
        response = await async_client.delete('/categories/delete/' + str(category_id),
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the category."}

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
