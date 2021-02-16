import pytest
from .operationtest import OperationTest
from pathlib import Path

class TestCart(OperationTest):
    prefix = "/carts"
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

        # create double variant
        response = await async_client.post(url,json={
            "va1_name": "Ukuran",
            "va2_name": "Warna",
            "va1_items": [
                {
                    "va1_option": "XL",
                    "va2_items": [
                        {"va2_option": "hitam", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "putih", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "merah", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "biru", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "hijau", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "jingga", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "cream", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "biru dongker", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "emas", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "orange", "va2_price": '29000', "va2_stock": '2'},
                    ]
                },
                {
                    "va1_option": "M",
                    "va2_items": [
                        {"va2_option": "hitam", "va2_price": '80000', "va2_stock": '2'},
                        {"va2_option": "putih", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "merah", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "biru", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "hijau", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "jingga", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "cream", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "biru dongker", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "emas", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "orange", "va2_price": '29000', "va2_stock": '2'},
                    ]
                },
                {
                    "va1_option": "S",
                    "va2_items": [
                        {"va2_option": "hitam", "va2_price": '80000', "va2_stock": '2'},
                        {"va2_option": "putih", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "merah", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "biru", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "hijau", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "jingga", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "cream", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "biru dongker", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "emas", "va2_price": '29000', "va2_stock": '2'},
                        {"va2_option": "orange", "va2_price": '29000', "va2_stock": '2'},
                    ]
                }
            ]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        # assign to variable
        self.__class__.double_variant = response.json()['ticket']

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
        assert response.json() == {"detail": "Successfully add a new item sub-category."}

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
                'ticket_variant': self.double_variant,
                'item_sub_category_id': str(item_sub_category_id)
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail":"Successfully add a new product."}

    def test_validation_put_product_to_cart(self,client):
        url = self.prefix + '/put-product'

        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant_id': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'qty': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'operation': assert x['msg'] == 'field required'

        # all field blank
        response = client.post(url,json={'variant_id': '', 'qty': '', 'operation': '', 'note': ''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant_id': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'qty': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'note': assert x['msg'] == 'ensure this value has at least 1 characters'

        # test limit value
        response = client.post(url,json={'variant_id': '200', 'qty': '200', 'note': 'a' * 200})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'note': assert x['msg'] == 'ensure this value has at most 100 characters'

        # check all field type data
        response = client.post(url,json={'variant_id': 123, 'qty': 123, 'operation': 'a', 'note': 123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant_id': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'qty': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'operation': assert x['msg'] == "unexpected value; permitted: 'update', 'create'"
            if x['loc'][-1] == 'note': assert x['msg'] == 'str type expected'

        # invalid format
        response = client.post(url,json={'variant_id': '1A', 'qty': '1A'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'variant_id': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'
            if x['loc'][-1] == 'qty': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'

    @pytest.mark.asyncio
    async def test_put_product_to_cart(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/put-product'

        user_id = await self.get_user_id(self.account_2['email'])
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)
        variant_product_one = await self.get_all_variant_by_product_id(product_id_one)
        variant_product_two = await self.get_all_variant_by_product_id(product_id_two)

        # variant not found
        response = await async_client.post(url,json={
            'variant_id': '99999999',
            'qty': '1',
            'operation': 'create'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Variant not found!"}

        # ===== operation cart create =====
        # stock is 0 and cart is None
        response = await async_client.post(url,json={
            'variant_id': str(variant_product_one[0]['id']),
            'qty': '1',
            'operation': 'create'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "The amount you input exceeds the available stock."}

        # stock is less than qty on cart
        response = await async_client.post(url,json={
            'variant_id': str(variant_product_two[0]['id']),
            'qty': '1',
            'operation': 'create'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "The product has been successfully added to the shopping cart."}
        assert await self.get_qty_cart(variant_product_two[0]['id'],user_id) == 1

        response = await async_client.post(url,json={
            'variant_id': str(variant_product_two[0]['id']),
            'qty': '1',
            'operation': 'create'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Shopping cart successfully updated."}
        assert await self.get_qty_cart(variant_product_two[0]['id'],user_id) == 2

        response = await async_client.post(url,json={
            'variant_id': str(variant_product_two[0]['id']),
            'qty': '1',
            'operation': 'create'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "This item has 2 stock left and you already have 2 in your basket."}

        # limit cart 20
        for key,value in enumerate(variant_product_two[1:21]):
            response = await async_client.post(url,json={
                'variant_id': str(value['id']),
                'qty': '1',
                'operation': 'create'
            },headers={'X-CSRF-TOKEN': csrf_access_token})
            if key != 19:
                assert response.status_code == 201
                assert response.json() == {"detail": "The product has been successfully added to the shopping cart."}
            else:
                assert response.status_code == 400
                assert response.json() == {"detail": "The basket can only contain 20 items. Delete some items to add others."}

        # ===== operation cart update =====
        # update qty on cart
        response = await async_client.post(url,json={
            'variant_id': str(variant_product_two[0]['id']),
            'qty': '1',
            'operation': 'update'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Shopping cart successfully updated."}
        assert await self.get_qty_cart(variant_product_two[0]['id'],user_id) == 1

        # put another cart to different user
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        for value in variant_product_two[:2]:
            response = await async_client.post(url,json={
                'variant_id': str(value['id']),
                'qty': '1',
                'operation': 'create'
            },headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail": "The product has been successfully added to the shopping cart."}

        # change some variant to 0
        await self.change_variant_stock_zero(variant_product_two[0]['id'])
        await self.change_variant_stock_zero(variant_product_two[1]['id'])

    def test_get_qty_and_item_on_cart(self,client):
        client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })

        url = self.prefix + '/qty-item-on-cart'

        response = client.get(url)
        assert response.status_code == 200
        assert 'user_id' in response.json()
        assert 'total_item' in response.json()
        assert 'total_qty' in response.json()
        assert 'ready_stock' in response.json()
        assert 'empty_stock' in response.json()

    def test_get_all_carts_from_nav(self,client):
        client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })

        url = self.prefix + '/from-nav'

        response = client.get(url)
        assert response.status_code == 200
        assert len(response.json()) == 20

        # check data exists and type data
        assert type(response.json()[0]['carts_id']) == str
        assert type(response.json()[0]['carts_qty']) == str
        assert type(response.json()[0]['variants_option']) == str
        assert type(response.json()[0]['variants_price']) == str
        assert response.json()[0]['variants_image'] is None
        assert type(response.json()[0]['products_name']) == str
        assert type(response.json()[0]['products_image_product']) == str
        assert type(response.json()[0]['products_weight']) == str

    def test_get_all_carts(self,client):
        client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })

        url = self.prefix + '/'

        # check all field type data
        response = client.get(url + '?stock=123')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'stock': assert x['msg'] == "unexpected value; permitted: 'empty', 'ready'"

        # stock none
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.json()) == 20

        # check data exists and type data
        assert type(response.json()[0]['carts_id']) == str
        assert response.json()[0]['carts_note'] is None
        assert type(response.json()[0]['carts_qty']) == str
        assert type(response.json()[0]['variants_id']) == str
        assert type(response.json()[0]['variants_option']) == str
        assert type(response.json()[0]['variants_price']) == str
        assert type(response.json()[0]['variants_stock']) == str
        assert response.json()[0]['variants_image'] is None
        assert type(response.json()[0]['variants_discount']) == int
        assert type(response.json()[0]['variants_discount_active']) == bool
        assert type(response.json()[0]['products_id']) == str
        assert type(response.json()[0]['products_name']) == str
        assert type(response.json()[0]['products_slug']) == str
        assert type(response.json()[0]['products_love']) == bool
        assert type(response.json()[0]['products_image_product']) == str
        assert response.json()[0]['products_preorder'] is None
        assert type(response.json()[0]['products_discount_status']) == str
        assert response.json()[0]['products_wholesale'] is None

        # stock empty
        response = client.get(url + '?stock=empty')
        assert response.status_code == 200
        assert len(response.json()) == 2

        # check data exists and type data
        assert type(response.json()[0]['carts_id']) == str
        assert response.json()[0]['carts_note'] is None
        assert type(response.json()[0]['carts_qty']) == str
        assert type(response.json()[0]['variants_id']) == str
        assert type(response.json()[0]['variants_option']) == str
        assert type(response.json()[0]['variants_price']) == str
        assert type(response.json()[0]['variants_stock']) == str
        assert response.json()[0]['variants_image'] is None
        assert type(response.json()[0]['variants_discount']) == int
        assert type(response.json()[0]['variants_discount_active']) == bool
        assert type(response.json()[0]['products_id']) == str
        assert type(response.json()[0]['products_name']) == str
        assert type(response.json()[0]['products_slug']) == str
        assert type(response.json()[0]['products_love']) == bool
        assert type(response.json()[0]['products_image_product']) == str
        assert response.json()[0]['products_preorder'] is None
        assert type(response.json()[0]['products_discount_status']) == str
        assert response.json()[0]['products_wholesale'] is None

        # ready stock
        response = client.get(url + '?stock=ready')
        assert response.status_code == 200
        assert len(response.json()) == 18

        # check data exists and type data
        assert type(response.json()[0]['carts_id']) == str
        assert response.json()[0]['carts_note'] is None
        assert type(response.json()[0]['carts_qty']) == str
        assert type(response.json()[0]['variants_id']) == str
        assert type(response.json()[0]['variants_option']) == str
        assert type(response.json()[0]['variants_price']) == str
        assert type(response.json()[0]['variants_stock']) == str
        assert response.json()[0]['variants_image'] is None
        assert type(response.json()[0]['variants_discount']) == int
        assert type(response.json()[0]['variants_discount_active']) == bool
        assert type(response.json()[0]['products_id']) == str
        assert type(response.json()[0]['products_name']) == str
        assert type(response.json()[0]['products_slug']) == str
        assert type(response.json()[0]['products_love']) == bool
        assert type(response.json()[0]['products_image_product']) == str
        assert response.json()[0]['products_preorder'] is None
        assert type(response.json()[0]['products_discount_status']) == str
        assert response.json()[0]['products_wholesale'] is None

    def test_validation_delete_cart(self,client):
        url = self.prefix + '/delete'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'cartIds': []})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'ensure this value has at least 1 items'
        # test limit value
        response = client.post(url,json={'cartIds': [str(x) for x in range(1,22)]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'ensure this value has at most 20 items'
        # check all field type data
        response = client.post(url,json={'cartIds': {}})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'value is not a valid list'

        response = client.post(url,json={'cartIds': [1]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'str type expected'
        # invalid format
        response = client.post(url,json={'cartIds': ['1A']})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'

    @pytest.mark.asyncio
    async def test_delete_cart(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/delete'

        user_id_one = await self.get_user_id(self.account_1['email'])
        user_id_two = await self.get_user_id(self.account_2['email'])
        cart_user_one = [data['id'] for data in await self.get_all_cart_by_user_id(user_id_one)]
        cart_user_two = [data['id'] for data in await self.get_all_cart_by_user_id(user_id_two)]

        # delete single
        response = await async_client.post(url,json={
            'cartIds': [str(cart_user_two[0])]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "1 items were removed."}
        assert cart_user_two[0] not in [data['id'] for data in await self.get_all_cart_by_user_id(user_id_two)]

        # delete multiple with wrong id and id that own by another user
        response = await async_client.post(url,json={
            'cartIds': [str(x) for x in [0] + cart_user_one + cart_user_two[:11]]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "14 items were removed."}
        assert cart_user_one == [data['id'] for data in await self.get_all_cart_by_user_id(user_id_one)]
        assert len([data['id'] for data in await self.get_all_cart_by_user_id(user_id_two)]) == 9

    def test_validation_move_to_wishlist(self,client):
        url = self.prefix + '/move-to-wishlist'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'cartIds': []})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'ensure this value has at least 1 items'
        # test limit value
        response = client.post(url,json={'cartIds': [str(x) for x in range(1,22)]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'ensure this value has at most 20 items'
        # check all field type data
        response = client.post(url,json={'cartIds': {}})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'value is not a valid list'

        response = client.post(url,json={'cartIds': [1]})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'str type expected'
        # invalid format
        response = client.post(url,json={'cartIds': ['1A']})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'cartIds': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'

    @pytest.mark.asyncio
    async def test_move_to_wishlist(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/move-to-wishlist'

        user_id_one = await self.get_user_id(self.account_1['email'])
        user_id_two = await self.get_user_id(self.account_2['email'])
        cart_user_one = [data['id'] for data in await self.get_all_cart_by_user_id(user_id_one)]
        cart_user_two = [data['id'] for data in await self.get_all_cart_by_user_id(user_id_two)]

        # move to wishlist single item
        response = await async_client.post(url,json={
            'cartIds': [str(cart_user_two[0])]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "1 items successfully moved to the wishlist."}
        assert cart_user_two[0] not in [data['id'] for data in await self.get_all_cart_by_user_id(user_id_two)]
        assert await self.get_len_of_wishlist_user(user_id_two) == 1

        # move to wishlist multiple item with wrong id and id that own by another user
        response = await async_client.post(url,json={
            'cartIds': [str(x) for x in [0] + cart_user_one + cart_user_two]
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "12 items successfully moved to the wishlist."}
        assert cart_user_one == [data['id'] for data in await self.get_all_cart_by_user_id(user_id_one)]
        assert [data['id'] for data in await self.get_all_cart_by_user_id(user_id_two)] == []
        assert await self.get_len_of_wishlist_user(user_id_two) == 1

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
