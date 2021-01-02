import pytest
from .operationtest import OperationTest

class TestComment(OperationTest):
    prefix = "/comments"
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

    def test_validation_create_comment(self,client):
        url = self.prefix + '/create'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'subject': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'comment_type': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'subject': '', 'comment_id': 0})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'subject': assert x['msg'] == 'ensure this value has at least 5 characters'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.post(url,json={'subject': 123, 'comment_id': '123', 'comment_type': 123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'subject': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'comment_type': assert x['msg'] == "unexpected value; permitted: 'product'"

    @pytest.mark.asyncio
    async def test_create_comment(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)
        # check user is not admin
        response = await async_client.post(url,json={
            'subject': self.name,
            'comment_id': product_id_one,
            'comment_type': 'product'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 403
        assert response.json() == {"detail": "Admin cannot create comments in their own product."}
        # user not admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # product not found
        response = await async_client.post(url,json={
            'subject': self.name,
            'comment_id': 99999999,
            'comment_type': 'product'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Product not found!"}

        response = await async_client.post(url,json={
            'subject': self.name,
            'comment_id': product_id_one,
            'comment_type': 'product'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Comment successfully added."}
        # cooldown 15 second
        response = await async_client.post(url,json={
            'subject': self.name,
            'comment_id': product_id_one,
            'comment_type': 'product'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 403
        assert response.json() == {"detail": "You've already added comment a moment ago. Please try again later."}
        # add comment again in another product
        response = await async_client.post(url,json={
            'subject': self.name2,
            'comment_id': product_id_two,
            'comment_type': 'product'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Comment successfully added."}

    def test_validation_get_all_comments(self,client):
        url = self.prefix + '/all-comments'
        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'comment_type': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?page=0&per_page=0&comment_id=0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.get(url + '?page=a&per_page=a&comment_id=a&comment_type=123')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'page': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'per_page': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'comment_type': assert x['msg'] == "unexpected value; permitted: 'product'"

    @pytest.mark.asyncio
    async def test_get_all_comments(self,async_client):
        url = self.prefix + '/all-comments'

        product_id_one = await self.get_product_id(self.name)
        response = await async_client.get(url + f'?page=1&per_page=1&comment_id={product_id_one}&comment_type=product')
        assert response.status_code == 200
        assert 'data' in response.json()
        assert 'total' in response.json()
        assert 'next_num' in response.json()
        assert 'prev_num' in response.json()
        assert 'page' in response.json()
        assert 'iter_pages' in response.json()

    def test_validation_delete_comment(self,client):
        url = self.prefix + '/delete/'
        # all field blank
        response = client.delete(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.delete(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_delete_comment(self,async_client):
        # user two login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/delete/'
        # set user one to guest
        await self.set_user_to_guest(self.account_1['email'])
        # comment not found
        response = await async_client.delete(url + '9' * 8,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Comment not found!"}
        # user one login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')
        # comment not match with current user
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)
        comment_id_one = await self.get_comment_id(self.name,product_id_one,'product')
        comment_id_two = await self.get_comment_id(self.name2,product_id_two,'product')

        response = await async_client.delete(url + str(comment_id_one),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "Comment not match with the current user."}
        # user two login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        # delete comment one
        response = await async_client.delete(url + str(comment_id_one),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Comment successfully deleted."}
        # delete comment two
        response = await async_client.delete(url + str(comment_id_two),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Comment successfully deleted."}

    @pytest.mark.asyncio
    async def test_delete_category(self,async_client):
        # set user one to admin again
        await self.set_user_to_admin(self.account_1['email'])

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
