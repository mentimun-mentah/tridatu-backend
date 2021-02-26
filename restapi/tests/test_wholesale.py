import pytest
from .operationtest import OperationTest

class TestWholeSale(OperationTest):
    prefix = "/wholesale"
    without_variant = None
    double_variant = None

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

    @pytest.mark.asyncio
    async def test_create_variant(self,async_client):
        url = '/variants/create-ticket'

        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        # create without
        response = await async_client.post(url,json={
            'va1_items': [{
                'va1_price': '1000',
                'va1_stock': '0',
                'va1_code': '1271521-899-SM',
                'va1_barcode': '889362033471'
            }]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        # assign to variable
        self.__class__.without_variant = response.json()['ticket']

        # create double variant
        response = await async_client.post(url,json={
            "va1_name": "Ukuran",
            "va2_name": "Warna",
            "va1_items": [
                {
                    "va1_option": "XL",
                    "va2_items": [
                        {
                            "va2_option": "hitam",
                            "va2_price": '29000',
                            "va2_stock": '2',
                        },
                        {
                            "va2_option": "putih",
                            "va2_price": '29000',
                            "va2_stock": '2',
                        }
                    ]
                },
                {
                    "va1_option": "M",
                    "va2_items": [
                        {
                            "va2_option": "hitam",
                            "va2_price": '80000',
                            "va2_stock": '2',
                        },
                        {
                            "va2_option": "putih",
                            "va2_price": '29000',
                            "va2_stock": '2',
                        }
                    ]
                }
            ]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        # assign to variable
        self.__class__.double_variant = response.json()['ticket']

    def test_validation_create_wholesale(self,client):
        url = self.prefix + '/create-ticket'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'items': assert x['msg'] == 'field required'

        # all field blank
        response = client.post(url,json={'variant': '', 'items': []})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'items': assert x['msg'] == 'ensure this value has at least 1 items'

        response = client.post(url,json={'variant': '', 'items': [{'min_qty': 0, 'price': ''}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'min_qty': assert x['msg'] == 'ensure this value is greater than 1'
            if x['loc'][-1] == 'price': assert x['msg'] == 'ensure this value has at least 1 characters'

        # test limit value
        response = client.post(url,json={'variant': 'a' * 200, 'items': [{'min_qty': f'{x}', 'price': f'{x}'} for x in range(10)]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'items': assert x['msg'] == 'ensure this value has at most 5 items'

        # check all field type data
        response = client.post(url,json={'variant': 123, 'items': {}})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'items': assert x['msg'] == 'value is not a valid list'

        response = client.post(url,json={'variant': 123, 'items': [{'min_qty': 'a', 'price': 123}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'min_qty': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'price': assert x['msg'] == 'str type expected'

        # invalid format
        response = client.post(url,json={'variant': 'asd', 'items': [{'min_qty': 1, 'price': '1A'}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'price': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'

        # variant not found
        response = client.post(url,json={'variant':'a', 'items': [{'min_qty': 2, 'price': '123'}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'variant not found'
            if x['loc'][-1] == 'items': assert x['msg'] == 'variant not found'
        # all price in variant must be same
        response = client.post(url,json={'variant': self.double_variant,'items': [{'min_qty': 2, 'price': '123'}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant': assert x['msg'] == 'wholesale prices are only available for all variant that are priced the same'
            if x['loc'][-1] == 'items': assert x['msg'] == 'variant not found'
        # price in items must be greater than 50% initial price from variant
        response = client.post(url,json={'variant': self.without_variant,'items': [{'min_qty': 2, 'price': '123'}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'items': assert x['msg'] == 'price 0: The price shall not be 50% lower than the initial price'

        response = client.post(url,json={'variant': self.without_variant,'items': [
            {'min_qty': 2, 'price': '800'},
            {'min_qty': 3, 'price': '499'},
            {'min_qty': 4, 'price': '500'}
        ]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'items': assert x['msg'] == 'price 1: The price shall not be 50% lower than the initial price'
        # min_qty must be greater than before
        response = client.post(url,json={'variant': self.without_variant,'items': [
            {'min_qty': 2, 'price': '800'},
            {'min_qty': 2, 'price': '700'},
            {'min_qty': 4, 'price': '600'}
        ]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'items': assert x['msg'] == 'min_qty 1: must be more > than before'
        # price must be lower than before
        response = client.post(url,json={'variant': self.without_variant,'items': [
            {'min_qty': 2, 'price': '800'},
            {'min_qty': 3, 'price': '800'},
            {'min_qty': 4, 'price': '600'}
        ]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'items': assert x['msg'] == 'price 1: The price must be less than the previous price'

    def test_create_wholesale(self,client):
        response = client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create-ticket'
        # check user is admin
        response = client.post(url,json={
            'variant': self.without_variant,
            'items': [{'min_qty': 2, 'price': '8000'}]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = client.post(url,json={
            'variant': self.without_variant,
            'items': [{'min_qty': 2, 'price': '8000'}]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert 'ticket' in response.json()

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
