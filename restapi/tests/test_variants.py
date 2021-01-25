import pytest
from .operationtest import OperationTest

class TestVariant(OperationTest):
    prefix = "/variants"

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

    def test_validation_create_variant(self,client):
        url = self.prefix + '/create-ticket'

        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'field required'

        response  = client.post(url,json={
            'va1_items': [{'va2_items': [{}]}]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va2_option': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'va2_price': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'va2_stock': assert x['msg'] == 'field required'

        # all field blank
        response = client.post(url,json={
            'va1_name': '',
            'va2_name': '',
            'va1_items': []
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_name': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'va2_name': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure this value has at least 1 items'

        response = client.post(url,json={
            'va1_items': [{
                'va1_option': '',
                'va1_price': 0,
                'va1_stock': -1,
                'va1_code': '',
                'va1_barcode': '',
                'va2_items': []
            }]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_option': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'va1_price': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'va1_stock': assert x['msg'] == 'ensure this value is greater than or equal to 0'
            if x['loc'][-1] == 'va1_code': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'va1_barcode': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'va2_items': assert x['msg'] == 'ensure this value has at least 1 items'

        response = client.post(url,json={
            'va1_items': [{
                'va2_items': [{
                    'va2_option': '',
                    'va2_price': 0,
                    'va2_stock': -1,
                    'va2_code': '',
                    'va2_barcode': ''
                }]
            }]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va2_option': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'va2_price': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'va2_stock': assert x['msg'] == 'ensure this value is greater than or equal to 0'
            if x['loc'][-1] == 'va2_code': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'va2_barcode': assert x['msg'] == 'ensure this value has at least 1 characters'

        # test limit value
        response = client.post(url,json={
            'va1_name': 'a' * 200,
            'va2_name': 'a' * 200,
            'va1_items': [{"va1_option": f"{x}", "va1_price": 1, "va1_stock": 0} for x in range(30)]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_name': assert x['msg'] == 'ensure this value has at most 15 characters'
            if x['loc'][-1] == 'va2_name': assert x['msg'] == 'ensure this value has at most 15 characters'
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure this value has at most 20 items'

        response = client.post(url,json={
            'va1_items': [{
                'va1_option': 'a' * 200,
                'va1_price': 200,
                'va1_stock': 200,
                'va1_code': 'a' * 200,
                'va1_barcode': 'a' * 200,
                'va2_items': [{"va2_option": f"{x}", "va2_price": 1, "va2_stock": 0} for x in range(30)]
            }]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_option': assert x['msg'] == 'ensure this value has at most 20 characters'
            if x['loc'][-1] == 'va1_code': assert x['msg'] == 'ensure this value has at most 50 characters'
            if x['loc'][-1] == 'va1_barcode': assert x['msg'] == 'ensure this value has at most 50 characters'
            if x['loc'][-1] == 'va2_items': assert x['msg'] == 'ensure this value has at most 20 items'

        response = client.post(url,json={
            'va1_items': [{
                'va2_items': [{
                    'va2_option': 'a' * 200,
                    'va2_price': 200,
                    'va2_stock': 200,
                    'va2_code': 'a' * 200,
                    'va2_barcode': 'a' * 200
                }]
            }]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va2_option': assert x['msg'] == 'ensure this value has at most 20 characters'
            if x['loc'][-1] == 'va2_code': assert x['msg'] == 'ensure this value has at most 50 characters'
            if x['loc'][-1] == 'va2_barcode': assert x['msg'] == 'ensure this value has at most 50 characters'

        # check all field type data
        response = client.post(url,json={
            'va1_name': 123,
            'va2_name': 123,
            'va1_items': {}
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_name': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'va2_name': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'value is not a valid list'

        response = client.post(url,json={
            'va1_items': [{
                'va1_option': 123,
                'va1_price': '123',
                'va1_stock': '123',
                'va1_code': 123,
                'va1_barcode': 123,
                'va2_items': {}
            }]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_option': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'va1_price': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'va1_stock': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'va1_code': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'va1_barcode': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'va2_items': assert x['msg'] == 'value is not a valid list'

        response = client.post(url,json={
            'va1_items': [{
                'va2_items': [{
                    'va2_option': 123,
                    'va2_price': '123',
                    'va2_stock': '123',
                    'va2_code': 123,
                    'va2_barcode': 123
                }]
            }]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va2_option': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'va2_price': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'va2_stock': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'va2_code': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'va2_barcode': assert x['msg'] == 'str type expected'

        # va1_name and va2_name is same
        response = client.post(url,json={'va1_name': 'warna', 'va2_name': 'warna'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va2_name': assert x['msg'] == 'Names cannot be the same.'

        # option duplicate in va1_items
        response = client.post(url,json={
            'va1_items': [{"va1_option": "XL", "va1_price": 1, "va1_stock": 0} for x in range(2)]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'the option must be different with each other'

        # option duplicate in va2_items
        response = client.post(url,json={
            'va1_items': [{
                'va2_items': [{"va2_option": "XL", "va2_price": 1, "va2_stock": 0} for x in range(2)]
            }]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va2_items': assert x['msg'] == 'the option must be different with each other'

        # without variant
        response = client.post(url,json={'va1_items': [{}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_price value is not null'

        response = client.post(url,json={'va1_items': [{'va1_price': 1}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_stock value is not null'

        # single variant
        response = client.post(url,json={'va1_items': [{'va1_option': 'XL'}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_name value is not null'

        response = client.post(url,json={'va1_name': 'ukuran', 'va1_items': [{}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_option at index 0 value is not null'

        response = client.post(url,json={'va1_name': 'ukuran', 'va1_items': [{'va1_option': 'XL'}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_price at index 0 value is not null'

        response = client.post(url,json={'va1_name': 'ukuran', 'va1_items': [{'va1_option': 'XL','va1_price': 1}]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_stock at index 0 value is not null'

        response = client.post(url,json={
            "va1_name": "Ukuran",
            "va1_items": [
                {"va1_option": "XL", "va1_price": 3000, "va1_stock": 1},
                {"va1_option": "M", "va1_price": 1000, "va1_stock": 1},
                {"va1_option": "S", "va1_price": 7001, "va1_stock": 1},
                {"va1_option": "XLL", "va1_price": 6000, "va1_stock": 1}
            ]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == \
                'the price difference between variations is too large, please set the price for the variation accordingly.'

        # double variant
        response = client.post(url,json={
            'va1_items': [{'va2_items': [{'va2_option':'XL', 'va2_price': 1, 'va2_stock': 0}]}]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_name value is not null'

        response = client.post(url,json={
            'va1_name': 'ukuran',
            'va1_items': [{'va2_items': [{'va2_option':'XL', 'va2_price': 1, 'va2_stock': 0}]}]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va2_name value is not null'

        response = client.post(url,json={
            'va1_name': 'warna',
            'va2_name': 'ukuran',
            'va1_items': [{'va2_items': [{'va2_option':'XL', 'va2_price': 1, 'va2_stock': 0}]}]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == 'ensure va1_option at index 0 value is not null'

        response = client.post(url,json={
            "va1_name": "Ukuran",
            "va2_name": "Warna",
            "va1_items": [
                {
                    "va1_option": "XL",
                    "va2_items": [
                        {
                            "va2_option": "hitam",
                            "va2_price": 4000,
                            "va2_stock": 2,
                        },
                        {
                            "va2_option": "putih",
                            "va2_price": 1000,
                            "va2_stock": 2,
                        }
                    ]
                },
                {
                    "va1_option": "M",
                    "va2_items": [
                        {
                            "va2_option": "hitam",
                            "va2_price": 7001,
                            "va2_stock": 2,
                        },
                        {
                            "va2_option": "putih",
                            "va2_price": 3000,
                            "va2_stock": 2,
                        }
                    ]
                }
            ]
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'va1_items': assert x['msg'] == \
                'the price difference between variations is too large, please set the price for the variation accordingly.'

    def test_create_variant(self,client):
        response = client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create-ticket'
        # check user is admin
        response = client.post(url,json={
            'va1_items': [{
                'va1_price': 11000,
                'va1_stock': 0,
                'va1_code': '1271521-899-SM',
                'va1_barcode': '889362033471'
            }]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        # create without
        response = client.post(url,json={
            'va1_items': [{
                'va1_price': 11000,
                'va1_stock': 0,
                'va1_code': '1271521-899-SM',
                'va1_barcode': '889362033471'
            }]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert 'ticket' in response.json()
        # create single variant
        response = client.post(url,json={
            "va1_name": "Ukuran",
            "va1_items": [
                {"va1_option": "XL", "va1_price": 3000, "va1_stock": 1, "va1_code": None, "va1_barcode": None},
                {"va1_option": "M", "va1_price": 1000, "va1_stock": 1, "va1_code": None, "va1_barcode": None},
                {"va1_option": "S", "va1_price": 7000, "va1_stock": 1, "va1_code": None, "va1_barcode": None},
                {"va1_option": "XLL", "va1_price": 6000, "va1_stock": 1, "va1_code": None, "va1_barcode": None}
            ]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert 'ticket' in response.json()
        # create double variant
        response = client.post(url,json={
            "va1_name": "Ukuran",
            "va2_name": "Warna",
            "va1_items": [
                {
                    "va1_option": "XL",
                    "va2_items": [
                        {
                            "va2_option": "hitam",
                            "va2_price": 4000,
                            "va2_stock": 2,
                            "va2_code": None,
                            "va2_barcode": None
                        },
                        {
                            "va2_option": "putih",
                            "va2_price": 1000,
                            "va2_stock": 2,
                            "va2_code": None,
                            "va2_barcode": None
                        }
                    ]
                },
                {
                    "va1_option": "M",
                    "va2_items": [
                        {
                            "va2_option": "hitam",
                            "va2_price": 7000,
                            "va2_stock": 2,
                            "va2_code": None,
                            "va2_barcode": None
                        },
                        {
                            "va2_option": "putih",
                            "va2_price": 3000,
                            "va2_stock": 2,
                            "va2_code": None,
                            "va2_barcode": None
                        }
                    ]
                }
            ]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert 'ticket' in response.json()

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
