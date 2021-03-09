import pytest
from .operationtest import OperationTest

class TestAddress(OperationTest):
    prefix = "/address"

    @pytest.mark.asyncio
    async def test_add_user(self,async_client):
        url = '/users/register'
        # register user
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
        # activated the user
        confirm_id = await self.get_confirmation(self.account_1['email'])
        await self.set_account_to_activated(confirm_id)

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
        assert response.json() == {"detail":"Check your email to activated your account."}
        # activated the user
        confirm_id = await self.get_confirmation(self.account_2['email'])
        await self.set_account_to_activated(confirm_id)

    def test_search_city_or_district(self,client):
        url = self.prefix + "/search/city-or-district"

        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?q=')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at least 3 characters'
        # test limit value
        response = client.get(url + '?q=' + 'a' * 200)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at most 100 characters'

        response = client.get(url + '?q=denpasar')
        assert response.status_code == 200
        assert len(response.json()) == 4

        # check data exists and type data
        assert type(response.json()[0]['value']) == str
        assert type(response.json()[0]['postal_code']) == list

    def test_validation_create_address(self,client):
        url = self.prefix + "/create"
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'region': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={
            "label": "",
            "receiver": "",
            "phone": "",
            "region": "",
            "postal_code": 0,
            "recipient_address": "",
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'region': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'ensure this value has at least 1 characters'
        # test limit value
        response = client.post(url,json={
            "label": "a" * 200,
            "receiver": "a" * 200,
            "phone": "a" * 200,
            "region": "a" * 200,
            "postal_code": 9999999,
            "recipient_address": "a" * 200,
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'ensure this value has at most 20 characters'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'ensure this value is less than 999999'
        # check all field type data
        response = client.post(url,json={
            "label": 123,
            "receiver": 123,
            "phone": 123,
            "region": 123,
            "postal_code": "123",
            "recipient_address": 123,
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'region': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'str type expected'
        # invalid phone number
        response = client.post(url,json={'phone': 'asdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "value is not a valid mobile phone number"

        response = client.post(url,json={'phone': '8762732'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "value is not a valid mobile phone number"

    def test_create_address(self,client):
        # user login
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'

        response = client.post(url,headers={"X-CSRF-TOKEN": csrf_access_token},json={
            "label": "string",
            "receiver": "string",
            "phone": "876781233",
            "region": "string",
            "postal_code": 1,
            "recipient_address": "string",
        })
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new address."}

    def test_my_address(self,client):
        url = self.prefix + '/my-address'
        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?page=0&per_page=0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.get(url + '?page=a&per_page=a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'value is not a valid integer'
        # user login
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })

        response = client.get(url + '?page=1&per_page=1')
        assert response.status_code == 200
        assert 'data' in response.json()
        assert 'total' in response.json()
        assert 'next_num' in response.json()
        assert 'prev_num' in response.json()
        assert 'page' in response.json()
        assert 'iter_pages' in response.json()

        # check data exists and type data
        assert type(response.json()['data'][0]['label']) == str
        assert type(response.json()['data'][0]['receiver']) == str
        assert type(response.json()['data'][0]['phone']) == str
        assert type(response.json()['data'][0]['region']) == str
        assert type(response.json()['data'][0]['postal_code']) == int
        assert type(response.json()['data'][0]['recipient_address']) == str
        assert type(response.json()['data'][0]['main_address']) == bool
        assert type(response.json()['data'][0]['id']) == str

    def test_validation_my_address_by_id(self,client):
        url = self.prefix + '/my-address/'
        # all field blank
        response = client.get(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.get(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_my_address_by_id(self,async_client):
        # user login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })

        url = self.prefix + '/my-address/'
        # address not found
        response = await async_client.get(url + '9' * 8)
        assert response.status_code == 404
        assert response.json() == {"detail": "Address not found!"}

        # address not match with current user
        user_id = await self.get_user_id(self.account_1['email'])
        address_id = await self.get_address_id(user_id)

        response = await async_client.get(url + str(address_id))
        assert response.status_code == 400
        assert response.json() == {"detail": "Address not match with the current user."}
        # change user login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })

        response = await async_client.get(url + str(address_id))
        assert response.status_code == 200
        assert 'label' in response.json()
        assert 'receiver' in response.json()
        assert 'phone' in response.json()
        assert 'region' in response.json()
        assert 'postal_code' in response.json()
        assert 'recipient_address' in response.json()
        assert 'main_address' in response.json()
        assert 'id' in response.json()

    @pytest.mark.asyncio
    async def test_validation_update_address(self,async_client):
        # validation path parameter
        url = self.prefix + '/update/'
        # all field blank
        response = await async_client.put(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = await async_client.put(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'value is not a valid integer'

        user_id = await self.get_user_id(self.account_1['email'])
        address_id = await self.get_address_id(user_id)
        # validation request body
        url = self.prefix + f'/update/{address_id}'
        # field required
        response = await async_client.put(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'region': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'field required'
        # all field blank
        response = await async_client.put(url,json={
            "label": "",
            "receiver": "",
            "phone": "",
            "region": "",
            "postal_code": 0,
            "recipient_address": "",
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'region': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'ensure this value has at least 1 characters'
        # test limit value
        response = await async_client.put(url,json={
            "label": "a" * 200,
            "receiver": "a" * 200,
            "phone": "a" * 200,
            "region": "a" * 200,
            "postal_code": 9999999,
            "recipient_address": "a" * 200,
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'ensure this value has at most 20 characters'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'ensure this value is less than 999999'
        # check all field type data
        response = await async_client.put(url,json={
            "label": 123,
            "receiver": 123,
            "phone": 123,
            "region": 123,
            "postal_code": "123",
            "recipient_address": 123,
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'region': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'str type expected'
        # invalid phone number
        response = await async_client.put(url,json={'phone': 'asdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "value is not a valid mobile phone number"

        response = await async_client.put(url,json={'phone': '8762732'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "value is not a valid mobile phone number"

    @pytest.mark.asyncio
    async def test_update_address(self,async_client):
        # user login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        data = {
            "label": "string2",
            "receiver": "string2",
            "phone": "8787878787",
            "region": "string2",
            "postal_code": 2,
            "recipient_address": "string2",
        }

        url = self.prefix + '/update/'
        # address not found
        response = await async_client.put(url + '9' * 8,json=data,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Address not found!"}

        # address not match with current user
        user_id = await self.get_user_id(self.account_1['email'])
        address_id = await self.get_address_id(user_id)

        response = await async_client.put(url + str(address_id),json=data,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "Address not match with the current user."}
        # change user login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = await async_client.put(url + str(address_id),json=data,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {'detail': 'Successfully update the address.'}

    def test_validation_main_address_true(self,client):
        url = self.prefix + '/main-address-true/'
        # all field blank
        response = client.put(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.put(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_main_adddress_true(self,async_client):
        # user login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/main-address-true/'
        # address not found
        response = await async_client.put(url + '9' * 8,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Address not found!"}
        # address not match with current user
        user_id = await self.get_user_id(self.account_1['email'])
        address_id = await self.get_address_id(user_id)

        response = await async_client.put(url + str(address_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "Address not match with the current user."}
        # change user login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = await async_client.put(url + str(address_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {'detail': 'Successfully set the address to main address.'}

    def test_validation_delete_address(self,client):
        url = self.prefix + '/delete/'
        # all field blank
        response = client.delete(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.delete(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'address_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_delete_address(self,async_client):
        # user login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/delete/'
        # address not found
        response = await async_client.delete(url + '9' * 8,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Address not found!"}
        # address not match with current user
        user_id = await self.get_user_id(self.account_1['email'])
        address_id = await self.get_address_id(user_id)

        response = await async_client.delete(url + str(address_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "Address not match with the current user."}
        # change user login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = await async_client.delete(url + str(address_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the address."}
        # check address has been deleted
        response = await async_client.delete(url + str(address_id),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Address not found!"}

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
