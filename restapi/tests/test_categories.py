import pytest
from .operationtest import OperationTest

class TestCategory(OperationTest):
    prefix = "/categories"

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

    def test_validation_create_category(self,client):
        url = self.prefix + '/create'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'name': ''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at least 3 characters'
        # test limit value
        response = client.post(url,json={'name': 'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.post(url,json={'name': 123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'str type expected'

    def test_create_category(self,client):
        response = client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        # check user is admin
        response = client.post(url,json={'name': self.name},headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = client.post(url,json={'name': self.name},headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new category."}

    def test_name_duplicate_create_category(self,client):
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        response = client.post(url,json={'name': self.name},headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "The name has already been taken."}

    def test_get_categories_with_children(self,client):
        url = self.prefix + '/'
        # all field blank
        response = client.get(url + '?q=')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at least 1 characters'

        # with search
        response = client.get(url + '?q=t')
        assert response.status_code == 200
        assert response.json() != []
        # without search
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() != []

    def test_validation_get_all_categories(self,client):
        url = self.prefix + '/all-categories'
        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'with_sub': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?q=')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at least 1 characters'
        # check all field type data
        response = client.get(url + '?with_sub=asd')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'with_sub': assert x['msg'] == 'value could not be parsed to a boolean'

    def test_get_all_categories(self,client):
        # with search
        url = self.prefix + '/all-categories?with_sub=false&q=t'
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() != []

        # without search
        url = self.prefix + '/all-categories?with_sub=false'
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() != []

    def test_validation_get_category_by_id(self,client):
        url = self.prefix + '/get-category/'
        # all field blank
        response = client.get(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.get(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_get_category_by_id(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })

        url = self.prefix + '/get-category/'
        category_id = await self.get_category_id(self.name)
        # check user is admin
        response = await async_client.get(url + str(category_id))
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        # category not found
        response = await async_client.get(url + '9' * 8)
        assert response.status_code == 404
        assert response.json() == {"detail": "Category not found!"}

        response = await async_client.get(url + str(category_id))
        assert response.status_code == 200
        assert 'id' in response.json()
        assert 'name' in response.json()

    def test_validation_update_category(self,client):
        url = self.prefix + '/update/'
        # field required
        response = client.put(url + '0',json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'field required'
        # all field blank
        response = client.put(url + '0',json={'name': ''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at least 3 characters'
        # check all field type data
        response = client.put(url + 'a',json={'name': 123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'name': assert x['msg'] == 'str type expected'
        # test limit value
        response = client.put(url + '1',json={'name': 'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at most 100 characters'

    @pytest.mark.asyncio
    async def test_update_category(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/update/'
        category_id = await self.get_category_id(self.name)
        # check user is admin
        response = await async_client.put(url + str(category_id),
            json={'name': self.name},
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
        # category not found
        response = await async_client.put(url + '9' * 8,
            json={'name': self.name},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Category not found!"}

        response = await async_client.put(url + str(category_id),
            json={'name': self.name},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully update the category."}

    @pytest.mark.asyncio
    async def test_name_duplicate_update_category(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        # create another category
        response = await async_client.post(url,
            json={'name': self.name2},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new category."}

        url = self.prefix + '/update/'
        category_id = await self.get_category_id(self.name2)
        # name already taken
        response = await async_client.put(url + str(category_id),
            json={'name': self.name},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "The name has already been taken."}

    def test_validation_delete_category(self,client):
        url = self.prefix + '/delete/'
        # all field blank
        response = client.delete(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.delete(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'category_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_delete_category(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/delete/'
        category_id = await self.get_category_id(self.name)
        # check user is admin
        response = await async_client.delete(url + str(category_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # category not found
        response = await async_client.delete(url + '9' * 8,headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Category not found!"}
        # delete category one
        response = await async_client.delete(url + str(category_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the category."}

        # delete category two
        category_id = await self.get_category_id(self.name2)
        response = await async_client.delete(url + str(category_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the category."}

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
