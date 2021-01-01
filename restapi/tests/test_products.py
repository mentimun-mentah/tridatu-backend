import pytest
from .operationtest import OperationTest
from pathlib import Path

class TestProduct(OperationTest):
    prefix = "/products"
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
                'va1_price': 11000,
                'va1_stock': 0,
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
                    'va1_price': 11000,
                    'va1_stock': 1,
                    'va1_code': None,
                    'va1_barcode': None
                },
                {
                    'va1_option': 'M',
                    'va1_price': 11000,
                    'va1_stock': 1,
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
        assert response.json() == {"detail": "Successfully add a new item sub-category."}

    def test_validation_create_product(self,client):
        url = self.prefix + '/create'

        # field required
        response = client.post(url,data={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'desc': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'condition': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'weight': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'item_sub_category_id': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'image_product': assert x['msg'] == 'field required'

        # all field blank
        response = client.post(url,data={
            'name': ' ',
            'desc': ' ',
            'weight': 0,
            'video': ' ',
            'preorder': 0,
            'ticket_variant': ' ',
            'item_sub_category_id': 0,
            'brand_id': 0
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at least 5 characters'
            if x['loc'][-1] == 'desc': assert x['msg'] == 'ensure this value has at least 20 characters'
            if x['loc'][-1] == 'weight': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'video': assert x['msg'] == 'ensure this value has at least 2 characters'
            if x['loc'][-1] == 'preorder': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'ensure this value has at least 5 characters'
            if x['loc'][-1] == 'item_sub_category_id': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'ensure this value is greater than 0'

        # test limit value
        response = client.post(url,data={
            'name': 'a' * 200,
            'desc': 'a' * 200,
            'weight': 200,
            'video': 'a' * 200,
            'preorder': 1000,
            'ticket_variant': 'a' * 200,
            'item_sub_category_id': 200,
            'brand_id': 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'video':
                assert x['msg'] == \
                    'string does not match regex \"^(http(s)?:\\/\\/)?((w){3}.)?youtu(be|.be)?(\\.com)?\\/.+\"'
            if x['loc'][-1] == 'preorder': assert x['msg'] == 'ensure this value is less than or equal to 500'
            if x['loc'][-1] == 'ticket_variant': assert x['msg'] == 'ensure this value has at most 100 characters'

        # check all field type data
        response = client.post(url,data={
            'condition': 123,
            'weight': 'asd',
            'video': 123,
            'preorder': 'asd',
            'item_sub_category_id': 'asd',
            'brand_id': 'asd'
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'condition': assert x['msg'] == 'value could not be parsed to a boolean'
            if x['loc'][-1] == 'weight': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'video':
                assert x['msg'] == \
                    'string does not match regex \"^(http(s)?:\\/\\/)?((w){3}.)?youtu(be|.be)?(\\.com)?\\/.+\"'
            if x['loc'][-1] == 'preorder': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'item_sub_category_id': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'brand_id': assert x['msg'] == 'value is not a valid integer'

        # check valid url youtube
        response = client.post(url,data={
            'video': 'https://www.facebook.com'
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'video':
                assert x['msg'] == \
                    'string does not match regex \"^(http(s)?:\\/\\/)?((w){3}.)?youtu(be|.be)?(\\.com)?\\/.+\"'

        # max file in list 10 image product
        response = client.post(url,files=[
            ("image_product",("image.jpeg", open(self.test_image_dir + 'image.jpeg','rb'),"image/jpg")) for x in range(20)
        ])
        assert response.status_code == 422
        assert response.json() == {"detail": "Maximal 10 images to be upload."}
        # max file in list 20 image variant
        response = client.post(url,files=[
            ("image_variant",("image.jpeg", open(self.test_image_dir + 'image.jpeg','rb'),"image/jpg")) for x in range(21)
        ])
        assert response.status_code == 422
        assert response.json() == {"detail": "Maximal 20 images to be upload."}

        # danger file extension
        with open(self.test_image_dir + 'test.txt','rb') as tmp:
            response = client.post(url,files={'image_product': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Cannot identify the image at index 1.'}

        with open(self.test_image_dir + 'test.txt','rb') as tmp:
            response = client.post(url,files={'image_variant': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Cannot identify the image at index 1.'}

        with open(self.test_image_dir + 'test.txt','rb') as tmp:
            response = client.post(url,files={'image_size_guide': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Cannot identify the image.'}

        # not valid file extension
        with open(self.test_image_dir + 'test.gif','rb') as tmp:
            response = client.post(url,files={'image_product': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'The image at index 1 must be between jpg, png, jpeg.'}

        with open(self.test_image_dir + 'test.gif','rb') as tmp:
            response = client.post(url,files={'image_variant': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'The image at index 1 must be between jpg, png, jpeg.'}

        with open(self.test_image_dir + 'test.gif','rb') as tmp:
            response = client.post(url,files={'image_size_guide': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Image must be between jpg, png, jpeg.'}

        # file cannot grater than 4 Mb
        with open(self.test_image_dir + 'size.png','rb') as tmp:
            response = client.post(url,files={'image_product': tmp})
            assert response.status_code == 413
            assert response.json() == {'detail': 'An image at index 1 cannot greater than 4 Mb.'}

        with open(self.test_image_dir + 'size.png','rb') as tmp:
            response = client.post(url,files={'image_variant': tmp})
            assert response.status_code == 413
            assert response.json() == {'detail': 'An image at index 1 cannot greater than 4 Mb.'}

        with open(self.test_image_dir + 'size.png','rb') as tmp:
            response = client.post(url,files={'image_size_guide': tmp})
            assert response.status_code == 413
            assert response.json() == {'detail': 'An image cannot greater than 4 Mb.'}

        # ticket variant not found
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = client.post(url,data={
                'name': 'a' * 20,
                'desc': 'a' * 20,
                'condition': False,
                'weight': 1,
                'ticket_variant': 'a' * 5,
                'item_sub_category_id': 1
            },files={'image_product': tmp})

            assert response.status_code == 404
            assert response.json() == {'detail': 'Ticket variant not found!'}
        # ticket without variant image filled
        response = client.post(url,data={
            'name': 'a' * 20,
            'desc': 'a' * 20,
            'condition': False,
            'weight': 1,
            'ticket_variant': self.without_variant,
            'item_sub_category_id': 1
        },files={
            'image_product': ('image.jpeg', open(self.test_image_dir + 'image.jpeg','rb'), 'image/jpg'),
            'image_variant': ('image.jpeg', open(self.test_image_dir + 'image.jpeg','rb'), 'image/jpg')
        })
        assert response.status_code == 422
        assert response.json() == {'detail': 'The image variant must not be filled.'}
        # ticket single or double variant not same length image with item in va1_items
        response = client.post(url,data={
            'name': 'a' * 20,
            'desc': 'a' * 20,
            'condition': False,
            'weight': 1,
            'ticket_variant': self.single_variant,
            'item_sub_category_id': 1
        },files={
            'image_product': ('image.jpeg', open(self.test_image_dir + 'image.jpeg','rb'), 'image/jpg'),
            'image_variant': ('image.jpeg', open(self.test_image_dir + 'image.jpeg','rb'), 'image/jpg')
        })
        assert response.status_code == 422
        assert response.json() == {'detail': 'You must fill all variant images or even without images.'}

    @pytest.mark.asyncio
    async def test_create_product(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        # check user is admin
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,data={
                'name': self.name,
                'desc': 'a' * 20,
                'condition': 'true',
                'weight': '1',
                'ticket_variant': self.without_variant,
                'item_sub_category_id': '1'
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 401
            assert response.json() == {'detail': 'Only users with admin privileges can do this action.'}

        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        # item_sub_category_id not found
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,data={
                'name': self.name,
                'desc': 'a' * 20,
                'condition': 'false',
                'weight': '1',
                'ticket_variant': self.without_variant,
                'item_sub_category_id': '99999'
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 404
            assert response.json() == {'detail': 'Item sub-category not found!'}
        # brand_id not found
        item_sub_category_id = await self.get_item_sub_category_id(self.name)
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,data={
                'name': self.name,
                'desc': 'a' * 20,
                'condition': 'false',
                'weight': '1',
                'ticket_variant': self.without_variant,
                'item_sub_category_id': str(item_sub_category_id),
                'brand_id': '99999'
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 404
            assert response.json() == {'detail': 'Brand not found!'}

        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,data={
                'name': self.name,
                'desc': 'a' * 20,
                'condition': 'false',
                'weight': '1',
                'ticket_variant': self.without_variant,
                'item_sub_category_id': str(item_sub_category_id)
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail":"Successfully add a new product."}

        # check folder exists in directory
        assert Path(self.product_dir + self.name).is_dir() is True

    @pytest.mark.asyncio
    async def test_name_duplicate_create_product(self,async_client):
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'

        item_sub_category_id = await self.get_item_sub_category_id(self.name)
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,data={
                'name': self.name,
                'desc': 'a' * 20,
                'condition': 'false',
                'weight': '1',
                'ticket_variant': self.without_variant,
                'item_sub_category_id': str(item_sub_category_id)
            },files={'image_product': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 400
            assert response.json() == {"detail":"The name has already been taken."}

    def test_validation_get_all_products(self,client):
        url = self.prefix + '/all-products'
        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?page=0&per_page=0&q=&p_min=0&p_max=0&item_sub_cat=&brand=')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'p_min': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'p_max': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'item_sub_cat': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'brand': assert x['msg'] == 'ensure this value has at least 1 characters'
        # check all field type data
        response = client.get(
            url +
            '?page=a&per_page=a&q=123&live=a&order_by=a&p_min=a' +
            '&p_max=a&item_sub_cat=a&brand=a&pre_order=a&condition=a'
        )
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'live': assert x['msg'] == 'value could not be parsed to a boolean'
            if x['loc'][-1] == 'order_by': assert x['msg'] == \
                "unexpected value; permitted: 'high_price', 'low_price', 'newest', 'visitor'"
            if x['loc'][-1] == 'p_min': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'p_max': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'pre_order': assert x['msg'] == 'value could not be parsed to a boolean'
            if x['loc'][-1] == 'condition': assert x['msg'] == 'value could not be parsed to a boolean'

    def test_get_all_products(self,client):
        url = self.prefix + '/all-products'

        response = client.get(url + '?page=1&per_page=1')
        assert response.status_code == 200
        assert 'data' in response.json()
        assert 'total' in response.json()
        assert 'next_num' in response.json()
        assert 'prev_num' in response.json()
        assert 'page' in response.json()
        assert 'iter_pages' in response.json()

    def test_validation_change_product_alive_archive(self,client):
        url = self.prefix + '/alive-archive/'
        # all field blank
        response = client.put(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.put(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'product_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_change_product_alive_archive(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/alive-archive/'
        product_id = await self.get_product_id(self.name)
        # check user is admin
        response = await async_client.put(url + str(product_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {"detail": "Only users with admin privileges can do this action."}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # product not found
        response = await async_client.put(url + '999999',headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Product not found!"}

        response = await async_client.put(url + str(product_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully change the product to alive."}
        # change product again
        response = await async_client.put(url + str(product_id),headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Successfully change the product to archive."}

    def test_search_products_by_name(self,client):
        url = self.prefix + '/search-by-name'
        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'limit': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?q=&limit=0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at least 1 characters'
            if x['loc'][-1] == 'limit': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.get(url + '?q=123&limit=asd')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'limit': assert x['msg'] == 'value is not a valid integer'

        response = client.get(url + '?q=t&limit=1')
        assert response.status_code == 200
        assert len(response.json()) == 1

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
