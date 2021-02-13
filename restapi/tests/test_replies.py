import pytest
from .operationtest import OperationTest
from pathlib import Path

class TestReply(OperationTest):
    prefix = "/replies"
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
                'va1_price': '11000',
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

    @pytest.mark.asyncio
    async def test_create_comment(self,async_client):
        # set user one to guest
        await self.set_user_to_guest(self.account_1['email'])

        url = '/comments/create'
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)

        # create comment using account 1
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = await async_client.post(url,json={
            'message': self.name,
            'commentable_id': str(product_id_one),
            'commentable_type': 'product'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Comment successfully added."}
        # create comment using account 2
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        response = await async_client.post(url,json={
            'message': self.name2,
            'commentable_id': str(product_id_two),
            'commentable_type': 'product'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Comment successfully added."}

    def test_validation_create_reply(self,client):
        url = self.prefix + '/create'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'message': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={'message': '', 'comment_id': ''})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'message': assert x['msg'] == 'ensure this value has at least 5 characters'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'ensure this value has at least 1 characters'
        # check all field type data
        response = client.post(url,json={'message': 123, 'comment_id': 123})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'message': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'str type expected'
        # invalid format
        response = client.post(url,json={'comment_id': '1A'})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'comment_id': assert x['msg'] == 'string does not match regex \"^[0-9]*$\"'

    @pytest.mark.asyncio
    async def test_create_reply(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)
        comment_id_one = await self.get_comment_id(self.name,product_id_one,'product')
        comment_id_two = await self.get_comment_id(self.name2,product_id_two,'product')

        # comment not found
        response = await async_client.post(url,json={
            'message': self.name,
            'comment_id': '99999999'
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Comment not found!"}

        response = await async_client.post(url,json={
            'message': self.name,
            'comment_id': str(comment_id_one)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully reply to this comment."}
        # cooldown 15 second
        response = await async_client.post(url,json={
            'message': self.name,
            'comment_id': str(comment_id_one)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 403
        assert response.json() == {"detail": "You've already added comment a moment ago. Please try again later."}
        # add reply again in another comment
        response = await async_client.post(url,json={
            'message': self.name2,
            'comment_id': str(comment_id_two)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 201
        assert response.json() == {"detail": "Successfully reply to this comment."}

    def test_validation_get_all_replies_in_comment(self,client):
        url = self.prefix + '/comments/'
        # wrong format path param
        response = client.get(url + 'a')
        assert response.status_code == 200
        assert response.json() == []

        response = client.get(url + '1,2,3')
        assert response.status_code == 200
        assert response.json() == []

        response = client.get(url + '1-')
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_all_replies_in_comment(self,async_client):
        url = self.prefix + '/comments/'
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)
        comment_id_one = await self.get_comment_id(self.name,product_id_one,'product')
        comment_id_two = await self.get_comment_id(self.name2,product_id_two,'product')

        # get replies in one comment
        response = await async_client.get(url + str(comment_id_one))
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

        # check data exists and type data
        assert type(response.json()['comments_id']) == str
        assert type(response.json()['comments_replies']) == list

        # get replies in multiple comment
        response = await async_client.get(url + str(comment_id_one) + '-' + str(comment_id_two))
        assert response.status_code == 200
        assert isinstance(response.json(), list) and response.json() != []

        # check data exists and type data
        assert type(response.json()[0]['comments_id']) == str
        assert type(response.json()[0]['comments_replies']) == list

    def test_validation_delete_reply(self,client):
        url = self.prefix + '/delete/'
        # all field blank
        response = client.delete(url + '0')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'reply_id': assert x['msg'] == 'ensure this value is greater than 0'
        # check all field type data
        response = client.delete(url + 'a')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'reply_id': assert x['msg'] == 'value is not a valid integer'

    @pytest.mark.asyncio
    async def test_delete_reply(self,async_client):
        # user two login
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/delete/'
        product_id_one = await self.get_product_id(self.name)
        product_id_two = await self.get_product_id(self.name2)
        comment_id_one = await self.get_comment_id(self.name,product_id_one,'product')
        comment_id_two = await self.get_comment_id(self.name2,product_id_two,'product')
        reply_id_one = await self.get_reply_id(self.name,comment_id_one)
        reply_id_two = await self.get_reply_id(self.name2,comment_id_two)

        # reply not found
        response = await async_client.delete(url + '9' * 8,headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 404
        assert response.json() == {"detail": "Reply not found!"}
        # reply not match with current user
        response = await async_client.delete(url + str(reply_id_one),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail": "Reply not match with the current user."}
        # user one login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        # delete reply one
        response = await async_client.delete(url + str(reply_id_one),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Reply successfully deleted."}
        # delete reply two
        response = await async_client.delete(url + str(reply_id_two),headers={"X-CSRF-TOKEN": csrf_access_token})
        assert response.status_code == 200
        assert response.json() == {"detail": "Reply successfully deleted."}

    @pytest.mark.asyncio
    async def test_delete_product(self,async_client):
        # set user one to admin again
        await self.set_user_to_admin(self.account_1['email'])

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
