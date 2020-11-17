import pytest
from .operationtest import OperationTest

class TestAddress(OperationTest):
    prefix = "/address"

    @pytest.mark.asyncio
    async def test_add_user(self,async_client):
        url = '/users/register'
        # register another user
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
        # activated the user
        confirm_id = await self.get_confirmation(self.account_1['email'])
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
            if x['loc'][-1] == 'main_address': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={
            "label": "",
            "receiver": "",
            "phone": "",
            "region": "",
            "postal_code": 0,
            "recipient_address": "",
            "main_address": ""
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'region': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'main_address': assert x['msg'] == 'value is not a valid boolean'
        # test limit value
        response = client.post(url,json={
            "label": "a" * 200,
            "receiver": "a" * 200,
            "phone": "a" * 200,
            "region": "a" * 200,
            "postal_code": 200,
            "recipient_address": "a" * 200,
            "main_address": "true"
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'ensure this value has at most 20 characters'
            if x['loc'][-1] == 'main_address': assert x['msg'] == 'value is not a valid boolean'
        # check all field type data
        response = client.post(url,json={
            "label": 123,
            "receiver": 123,
            "phone": 123,
            "region": 123,
            "postal_code": "123",
            "recipient_address": 123,
            "main_address": "false"
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'label': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'receiver': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'phone': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'region': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'postal_code': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'recipient_address': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'main_address': assert x['msg'] == 'value is not a valid boolean'
        # invalid phone number
        response = client.post(url,json={'phone': 'asdasd'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "Please provide a valid mobile phone number"

        response = client.post(url,json={'phone': '8762732'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'phone':
                assert x['msg'] == "Please provide a valid mobile phone number"

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
            "main_address": True
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
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = client.get(url + '?page=1&per_page=1',headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert len(response.json()['data']) == 1
        assert response.json()['total'] == 1
        assert response.json()['next_num'] is None
        assert response.json()['prev_num'] is None
        assert response.json()['page'] == 1
        assert response.json()['iter_pages'] == [1]

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
