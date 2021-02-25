import pytest
from .operationtest import OperationTest
from datetime import datetime, timedelta
from pathlib import Path
from pytz import timezone
from config import settings

tz = timezone(settings.timezone)
tf = '%d %b %Y %H:%M'

class TestDiscount(OperationTest):
    prefix = "/discounts"
    without_variant = None
    single_variant = None

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

        # create single variant
        response = await async_client.post(url,json={
            'va1_name': 'ukuran',
            'va1_items': [
                {
                    'va1_option': 'XL',
                    'va1_price': '11000',
                    'va1_stock': '1',
                    'va1_code': None,
                    'va1_barcode': None
                },
                {
                    'va1_option': 'M',
                    'va1_price': '11000',
                    'va1_stock': '1',
                    'va1_code': None,
                    'va1_barcode': None
                }
            ]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        # assign to variable
        self.__class__.single_variant = response.json()['ticket']

    @pytest.mark.asyncio
    async def test_create_item_sub_category(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # create category
        response = await async_client.post('/categories/create',
            json={'name': self.name},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new category."}
        # create sub category
        category_id = await self.get_category_id(self.name)
        response = await async_client.post('/sub-categories/create',
            json={'name': self.name,'category_id': category_id},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new sub-category."}
        # create item sub category
        sub_category_id = await self.get_sub_category_id(self.name)
        response = await async_client.post('/item-sub-categories/create',
            json={'name': self.name, 'sub_category_id': sub_category_id},
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully add a new item-sub-category."}

    @pytest.mark.asyncio
    async def test_create_product(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        item_sub_category_id = await self.get_item_sub_category_id(self.name)
        # create product 1
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post('/products/create',data={
                'name': self.name,
                'desc': 'a' * 20,
                'condition': 'false',
                'weight': '1',
                'ticket_variant': self.without_variant,
                'item_sub_category_id': str(item_sub_category_id)
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail":"Successfully add a new product."}
        # create product 2
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post('/products/create',data={
                'name': self.name2,
                'desc': 'a' * 20,
                'condition': 'false',
                'weight': '1',
                'ticket_variant': self.single_variant,
                'item_sub_category_id': str(item_sub_category_id)
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail":"Successfully add a new product."}

    @pytest.mark.asyncio
    async def test_set_product_live(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)

        # set product one to alive
        response = await async_client.put('/products/alive-archive/' + str(product_id_one),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully change the product to alive."}
        # set product two to alive
        response = await async_client.put('/products/alive-archive/' + str(product_id_two),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully change the product to alive."}

    @pytest.mark.asyncio
    async def test_update_variant_ticket(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)

        # get ticket variant for without_variant & without_variant_discount
        response = await async_client.get(self.prefix + f'/get-discount/{product_id_one}')
        without_variant = response.json()['products_variant']

        response = await async_client.post('/variants/create-ticket',json=without_variant,headers={'X-CSRF-TOKEN': csrf_access_token})
        self.__class__.without_variant = response.json()['ticket']

        without_variant['va1_items'][0].update({'va1_discount': 1,'va1_discount_active': True})
        response = await async_client.post('/variants/create-ticket',json=without_variant,headers={'X-CSRF-TOKEN': csrf_access_token})
        self.__class__.without_variant_discount = response.json()['ticket']

        # get ticket variant for single_variant
        response = await async_client.get(self.prefix + f'/get-discount/{product_id_two}')
        single_variant = response.json()['products_variant']
        response = await async_client.post('/variants/create-ticket',json=single_variant,headers={'X-CSRF-TOKEN': csrf_access_token})
        self.__class__.single_variant = response.json()['ticket']

    def test_validation_get_all_discounts(self,client):
        url = self.prefix + '/all-discounts'
        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?page=0&per_page=0&q=&status=')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at least 1 characters'
        # check all field type data
        response = client.get(url + '?page=a&per_page=a&q=123&status=123')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'status': assert x['msg'] == "unexpected value; permitted: 'ongoing', 'will_come', 'not_active', 'have_ended'"

    @pytest.mark.asyncio
    async def test_get_all_discounts(self,async_client):
        url = self.prefix + '/all-discounts'

        # check user is admin
        response = await async_client.post('/users/login',json={'email': self.account_2['email'],'password': self.account_2['password']})
        response = await async_client.get(url + '?page=1&per_page=1')
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}

        # user admin login
        response = await async_client.post('/users/login',json={'email': self.account_1['email'],'password': self.account_1['password']})

        discount_start = datetime.now(tz) + timedelta(minutes=1)
        discount_end = datetime.now(tz) + timedelta(hours=1,minutes=1)
        # check product discount not_active
        response = await async_client.get(url + '?page=1&per_page=1&status=not_active')
        assert response.status_code == 200
        assert response.json()['data'][0]['products_name'] == self.name2
        assert response.json()['data'][0]['products_discount_status'] == 'not_active'
        # check product discount will_come
        await self.update_product_by_name(self.name,**{
            'discount_start': discount_start.replace(tzinfo=None),
            'discount_end': discount_end.replace(tzinfo=None)
        })

        response = await async_client.get(url + '?page=1&per_page=1&status=will_come')
        assert response.status_code == 200
        assert response.json()['data'][0]['products_name'] == self.name
        assert response.json()['data'][0]['products_discount_status'] == 'will_come'
        # check product discount ongoing
        await self.update_product_by_name(self.name,**{
            'discount_start': (discount_start - timedelta(minutes=1)).replace(tzinfo=None),
            'discount_end': (discount_end + timedelta(hours=1,minutes=1)).replace(tzinfo=None)
        })

        response = await async_client.get(url + '?page=1&per_page=1&status=ongoing')
        assert response.status_code == 200
        assert response.json()['data'][0]['products_name'] == self.name
        assert response.json()['data'][0]['products_discount_status'] == 'ongoing'
        # check product discount have_ended
        await self.update_product_by_name(self.name,**{
            'discount_start': (discount_start - timedelta(hours=2,minutes=1)).replace(tzinfo=None),
            'discount_end': (discount_end - timedelta(hours=1,minutes=1)).replace(tzinfo=None)
        })

        response = await async_client.get(url + '?page=1&per_page=1&status=have_ended')
        assert response.status_code == 200
        assert response.json()['data'][0]['products_name'] == self.name
        assert response.json()['data'][0]['products_discount_status'] == 'have_ended'

        # check data is correct
        response = await async_client.get(url + '?page=1&per_page=1')
        assert response.status_code == 200
        assert 'data' in response.json()
        assert 'total' in response.json()
        assert 'next_num' in response.json()
        assert 'prev_num' in response.json()
        assert 'page' in response.json()
        assert 'iter_pages' in response.json()

        # check data exists and type data
        assert type(response.json()['data'][0]['products_id']) == str
        assert type(response.json()['data'][0]['products_name']) == str
        assert type(response.json()['data'][0]['products_slug']) == str
        assert type(response.json()['data'][0]['products_image_product']) == str
        assert type(response.json()['data'][0]['products_discount_start']) == str
        assert type(response.json()['data'][0]['products_discount_end']) == str
        assert type(response.json()['data'][0]['products_discount_status']) == str
        assert type(response.json()['data'][0]['variants_min_price']) == str
        assert type(response.json()['data'][0]['variants_max_price']) == str
        assert type(response.json()['data'][0]['variants_discount']) == int

    def test_validation_get_discount_product(self,client):
        url = self.prefix + '/get-discount/'
        # all field blank
        response = client.get(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.get(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_get_discount_product(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })

        url = self.prefix + '/get-discount/'
        product_id = await self.get_product_id(self.name)
        # check user is admin
        response = await async_client.get(url + str(product_id))
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        # product not found
        response = await async_client.get(url + '999999')
        assert response.status_code == 404
        assert response.json() == {"detail": "Product not found!"}

        response = await async_client.get(url + str(product_id))
        assert response.status_code == 200
        assert 'products_name' in response.json()
        assert 'products_discount_start' in response.json()
        assert 'products_discount_end' in response.json()
        assert 'products_variant' in response.json()

    def test_validation_create_discount_product(self,client):
        url = self.prefix + '/create'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'discount_start': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'discount_end': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={
            'product_id': '',
            'ticket_variant': '',
            'discount_start': '',
            'discount_end': ''
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'discount_start': assert x['msg'] == "time data '' does not match format '%d %b %Y %H:%M'"
            if x['loc'][-1] == 'discount_end': assert x['msg'] == "time data '' does not match format '%d %b %Y %H:%M'"
        # test limit value
        response = client.post(url,json={
            'product_id': '200',
            'ticket_variant': 'a' * 200,
            'discount_start': 'a' * 200,
            'discount_end': 'a' * 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.post(url,json={
            'product_id': 200,
            'ticket_variant': 200,
            'discount_start': 200,
            'discount_end': 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'discount_start': assert x['msg'] == "strptime() argument 1 must be str, not int"
            if x['loc'][-1] == 'discount_end': assert x['msg'] == "strptime() argument 1 must be str, not int"
        # invalid format
        response = client.post(url,json={'product_id': '1A'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'

        discount_start = datetime.now(tz) + timedelta(minutes=1)
        discount_end = datetime.now(tz) + timedelta(hours=1,minutes=1)
        # discount start must be after current time
        response = client.post(url,json={
            'discount_start': format(discount_start - timedelta(minutes=2),tf),
            'discount_end': format(discount_end,tf)
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'discount_start': assert x['msg'] == 'the start time must be after the current time'
        # discount_end must be longer one hour than start time
        response = client.post(url,json={
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end - timedelta(minutes=30),tf)
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'discount_end': assert x['msg'] == 'the expiration time must be at least one hour longer than the start time'
        # discount_end cannot less than current time
        response = client.post(url,json={
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end - timedelta(days=30),tf)
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'discount_end': assert x['msg'] == 'the expiration time must be at least one hour longer than the start time'
        # discount_end must be less than 180 days
        response = client.post(url,json={
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end + timedelta(days=181),tf)
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'discount_end': assert x['msg'] == 'promo period must be less than 180 days'

    @pytest.mark.asyncio
    async def test_create_discount_product(self,async_client):
        # set discount product to none again
        await self.update_product_by_name(self.name,**{'discount_start': None, 'discount_end': None})

        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        product_id = await self.get_product_id(self.name)

        discount_start = datetime.now(tz) + timedelta(minutes=1)
        discount_end = datetime.now(tz) + timedelta(hours=1,minutes=1)
        # check user is admin
        response = await async_client.post(url,json={
            'product_id': str(product_id),
            'ticket_variant': self.without_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {'detail': 'Only users with admin privileges can do this action.'}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # product not found
        response = await async_client.post(url,json={
            'product_id': '999999',
            'ticket_variant': self.without_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {'detail': 'Product not found!'}
        # ticket variant not found
        response = await async_client.post(url,json={
            'product_id': str(product_id),
            'ticket_variant': 'a' * 20,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {'detail': 'Ticket variant not found!'}
        # variant not same with product
        response = await async_client.post(url,json={
            'product_id': str(product_id),
            'ticket_variant': self.single_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Variant not same with product.'}

        response = await async_client.post(url,json={
            'product_id': str(product_id),
            'ticket_variant': self.without_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully set discount on product."}

        # if variant doesn't have discount active still can create discount
        response = await async_client.post(url,json={
            'product_id': str(product_id),
            'ticket_variant': self.without_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully set discount on product."}

        # set discount on product
        response = await async_client.post(url,json={
            'product_id': str(product_id),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully set discount on product."}

        # product already has discount
        response = await async_client.post(url,json={
            'product_id': str(product_id),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "Product already has discount."}

    def test_validation_update_discount_product(self,client):
        url = self.prefix + '/update'
        # field required
        response = client.put(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'discount_start': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'discount_end': assert x['msg'] == 'field required'
        # all field blank
        response = client.put(url,json={
            'product_id': '',
            'ticket_variant': '',
            'discount_start': '',
            'discount_end': ''
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'discount_start': assert x['msg'] == "time data '' does not match format '%d %b %Y %H:%M'"
            if x['loc'][-1] == 'discount_end': assert x['msg'] == "time data '' does not match format '%d %b %Y %H:%M'"
        # test limit value
        response = client.put(url,json={
            'product_id': '200',
            'ticket_variant': 'a' * 200,
            'discount_start': 'a' * 200,
            'discount_end': 'a' * 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.put(url,json={
            'product_id': 200,
            'ticket_variant': 200,
            'discount_start': 200,
            'discount_end': 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'discount_start': assert x['msg'] == "strptime() argument 1 must be str, not int"
            if x['loc'][-1] == 'discount_end': assert x['msg'] == "strptime() argument 1 must be str, not int"
        # invalid format
        response = client.put(url,json={'product_id': '1A'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'

    @pytest.mark.asyncio
    async def test_update_discount_product(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/update'
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)

        discount_start = datetime.now(tz) + timedelta(minutes=1)
        discount_end = datetime.now(tz) + timedelta(hours=1,minutes=1)
        # check user is admin
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {'detail': 'Only users with admin privileges can do this action.'}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # product not found
        response = await async_client.put(url,json={
            'product_id': '999999',
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {'detail': 'Product not found!'}
        # ticket variant not found
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': 'a' * 20,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {'detail': 'Ticket variant not found!'}
        # product doesn't have discount
        response = await async_client.put(url,json={
            'product_id': str(product_id_two),
            'ticket_variant': self.single_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {'detail': 'You must set a discount on the product before update it.'}
        # variant not same with product
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.single_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Variant not same with product.'}

        # discount start must be after set start time
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start - timedelta(minutes=5), tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 422
        assert response.json() == {'detail': 'The new start time must be after the set start time.'}
        # discount_end must be longer one hour than start time
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end - timedelta(minutes=5), tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 422
        assert response.json() == {'detail': 'The expiration time must be at least one hour longer than the start time.'}
        # discount_end cannot less than set start time
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end - timedelta(days=30), tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 422
        assert response.json() == {'detail': 'The expiration time must be at least one hour longer than the start time.'}
        # discount_end must be less than 180 days
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end + timedelta(days=181), tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 422
        assert response.json() == {'detail': 'Promo period must be less than 180 days.'}

        # set product to ongoing
        await self.update_product_by_name(self.name,**{
            'discount_start': (discount_start - timedelta(minutes=1)).replace(tzinfo=None),
            'discount_end': (discount_end + timedelta(hours=1,minutes=1)).replace(tzinfo=None)
        })
        # check discount start is set from db when promo is ongoing
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant_discount,
            'discount_start': format(discount_start - timedelta(days=30), tf),
            'discount_end': format(discount_end + timedelta(minutes=5), tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {'detail': 'Successfully updated discount on product.'}

        # when product doesn't have active promo then set product to not_active
        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {'detail': 'Successfully updated discount on product.'}

        response = await async_client.put(url,json={
            'product_id': str(product_id_one),
            'ticket_variant': self.without_variant,
            'discount_start': format(discount_start, tf),
            'discount_end': format(discount_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {'detail': 'You must set a discount on the product before update it.'}

    def test_validation_non_active_discount(self,client):
        url = self.prefix + '/non-active/'
        # all field blank
        response = client.delete(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.delete(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_non_active_discount(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/non-active/'
        product_id = await self.get_product_id(self.name)
        # check user is admin
        response = await async_client.delete(url + str(product_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # product not found
        response = await async_client.delete(url + '9' * 8,headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Product not found!"}

        response = await async_client.delete(url + str(product_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {'detail': 'Successfully unset discount on the product.'}

    @pytest.mark.asyncio
    async def test_delete_product(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # delete product one
        product_id = await self.get_product_id(self.name)
        response = await async_client.delete('/products/delete/' + str(product_id),
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the product."}
        # check folder has been delete in directory
        assert Path(self.product_dir + self.name + 'a').is_dir() is False

        product_id = await self.get_product_id(self.name2)
        # delete product two
        response = await async_client.delete('/products/delete/' + str(product_id),
            headers={'X-CSRF-TOKEN': csrf_access_token}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully delete the product."}
        # check folder has been delete in directory
        assert Path(self.product_dir + self.name2).is_dir() is False

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
