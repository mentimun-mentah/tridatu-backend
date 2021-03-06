import pytest
from .operationtest import OperationTest
from pathlib import Path
from datetime import datetime, timedelta
from pytz import timezone
from config import settings

tz = timezone(settings.timezone)
tf = '%d %b %Y %H:%M'

class TestPromo(OperationTest):
    prefix = "/promos"

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

    def test_validation_create_promo(self,client):
        url = self.prefix + '/create'

        # field required
        response = client.post(url,data={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'seen': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'period_start': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'period_end': assert x['msg'] == 'field required'

        # all field blank
        response = client.post(url,data={
            'name': ' ',
            'desc': ' ',
            'terms_condition': ' ',
            'period_start': ' ',
            'period_end': ' '
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at least 5 characters'
            if x['loc'][-1] == 'desc': assert x['msg'] == 'ensure this value has at least 5 characters'
            if x['loc'][-1] == 'terms_condition': assert x['msg'] == 'ensure this value has at least 5 characters'

        # test limit value
        response = client.post(url,data={
            'name': 'a' * 200,
            'desc': 'a' * 200,
            'terms_condition': 'a' * 200,
            'period_start': 'a' * 200,
            'period_end': 'a' * 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'name': assert x['msg'] == 'ensure this value has at most 100 characters'

        # check all field type data
        response = client.post(url,data={
            'name': 123,
            'desc': 123,
            'terms_condition': 123,
            'seen': 123,
            'period_start': 123,
            'period_end': 123
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'seen': assert x['msg'] == 'value could not be parsed to a boolean'

        # danger file extension
        with open(self.test_image_dir + 'test.txt','rb') as tmp:
            response = client.post(url,data={
                'name': 'a' * 5,
                'seen': False,
                'period_start': 'a' * 5,
                'period_end': 'a' * 5
            },files={'image': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Cannot identify the image.'}
        # not valid file extension
        with open(self.test_image_dir + 'test.gif','rb') as tmp:
            response = client.post(url,data={
                'name': 'a' * 5,
                'seen': False,
                'period_start': 'a' * 5,
                'period_end': 'a' * 5
            },files={'image': tmp})
            assert response.status_code == 422
            assert response.json() == {'detail': 'Image must be between jpg, png, jpeg.'}
        # file cannot grater than 4 Mb
        with open(self.test_image_dir + 'size.png','rb') as tmp:
            response = client.post(url,data={
                'name': 'a' * 5,
                'seen': False,
                'period_start': 'a' * 5,
                'period_end': 'a' * 5
            },files={'image': tmp})
            assert response.status_code == 413
            assert response.json() == {'detail':'An image cannot greater than 4 Mb.'}

        # desc, terms_condition and image is required if seen True
        response = client.post(url,data={
            'name': 'a' * 5,
            'seen': True,
            'period_start': 'a' * 5,
            'period_end': 'a' * 5
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "Please fill desc field."}

        response = client.post(url,data={
            'name': 'a' * 5,
            'desc': 'a' * 5,
            'seen': True,
            'period_start': 'a' * 5,
            'period_end': 'a' * 5
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "Please fill terms_condition field."}

        response = client.post(url,data={
            'name': 'a' * 5,
            'desc': 'a' * 5,
            'terms_condition': 'a' * 5,
            'seen': True,
            'period_start': 'a' * 5,
            'period_end': 'a' * 5
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "Please fill image field."}

        # invalid time format period_start & period_end
        response = client.post(url,data={
            'name': 'a' * 5,
            'seen': False,
            'period_start': 'a',
            'period_end': 'b'
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "Time data 'a' does not match format '%d %b %Y %H:%M'"}

        response = client.post(url,data={
            'name': 'a' * 5,
            'seen': False,
            'period_start': '19 May 1999 12:00',
            'period_end': 'b'
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "Time data 'b' does not match format '%d %b %Y %H:%M'"}

        period_start = datetime.now(tz) + timedelta(minutes=1)
        period_end = datetime.now(tz) + timedelta(days=1,minutes=1)
        # period_start must be after current time
        response = client.post(url,data={
            'name': 'a' * 5,
            'seen': False,
            'period_start': format(period_start - timedelta(minutes=2),tf),
            'period_end': format(period_end,tf)
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "The start time must be after the current time."}
        # period_end must be longer one day than start time
        response = client.post(url,data={
            'name': 'a' * 5,
            'seen': False,
            'period_start': format(period_start,tf),
            'period_end': format(period_end - timedelta(minutes=30),tf)
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "The expiration time must be at least one day longer than the start time."}
        # period_end cannot less than current time
        response = client.post(url,data={
            'name': 'a' * 5,
            'seen': False,
            'period_start': format(period_start,tf),
            'period_end': format(period_end - timedelta(days=30),tf)
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "The expiration time must be at least one day longer than the start time."}
        # period_end must be less than 180 days
        response = client.post(url,data={
            'name': 'a' * 5,
            'seen': False,
            'period_start': format(period_start,tf),
            'period_end': format(period_end + timedelta(days=181),tf)
        })
        assert response.status_code == 422
        assert response.json() == {"detail": "Promo period must be less than 180 days."}

    @pytest.mark.asyncio
    async def test_create_promo(self,async_client):
        response = await async_client.post('/users/login',json={
            'email': self.account_2['email'],
            'password': self.account_2['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'

        period_start = datetime.now(tz) + timedelta(minutes=1)
        period_end = datetime.now(tz) + timedelta(days=1,minutes=1)

        # check user is admin
        response = await async_client.post(url,data={
            'name': self.name,
            'seen': 'false',
            'period_start': format(period_start, tf),
            'period_end': format(period_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 401
        assert response.json() == {'detail': 'Only users with admin privileges can do this action.'}
        # user admin login
        response = await async_client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        # create promo 1
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,data={
                'name': self.name,
                'desc': 'a' * 5,
                'terms_condition': 'a' * 5,
                'seen': 'true',
                'period_start': format(period_start, tf),
                'period_end': format(period_end, tf),
            },files={'image': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail": "Successfully add a new promo."}
        # check image exists in directory
        image = await self.get_promo_image(self.name)
        assert Path(self.promo_dir + image).is_file() is True

        # create promo 2
        with open(self.test_image_dir + 'image.jpeg','rb') as tmp:
            response = await async_client.post(url,data={
                'name': self.name2,
                'desc': 'a' * 5,
                'terms_condition': 'a' * 5,
                'seen': 'false',
                'period_start': format(period_start, tf),
                'period_end': format(period_end, tf),
            },files={'image': tmp},headers={'X-CSRF-TOKEN': csrf_access_token})
            assert response.status_code == 201
            assert response.json() == {"detail": "Successfully add a new promo."}
        # check image doesn't exists in db
        assert await self.get_promo_image(self.name2) is None

    def test_name_duplicate_create_promo(self,client):
        # user admin login
        response = client.post('/users/login',json={
            'email': self.account_1['email'],
            'password': self.account_1['password']
        })
        csrf_access_token = response.cookies.get('csrf_access_token')

        url = self.prefix + '/create'

        period_start = datetime.now(tz) + timedelta(minutes=1)
        period_end = datetime.now(tz) + timedelta(days=1,minutes=1)

        response = client.post(url,data={
            'name': self.name,
            'seen': 'false',
            'period_start': format(period_start, tf),
            'period_end': format(period_end, tf)
        },headers={'X-CSRF-TOKEN': csrf_access_token})
        assert response.status_code == 400
        assert response.json() == {"detail":"The name has already been taken."}

    @pytest.mark.asyncio
    async def test_delete_user_from_db(self,async_client):
        await self.delete_user_from_db()
