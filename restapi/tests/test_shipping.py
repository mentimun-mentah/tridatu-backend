class TestShipping:
    prefix = "/shipping"

    def test_search_shipping_city_or_district(self,client):
        url = self.prefix + "/search/city-or-district"

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
        # test limit value
        response = client.get(url + '?q=' + 'a' * 200)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.get(url + '?q=123&limit=asd')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'limit': assert x['msg'] == 'value is not a valid integer'

        response = client.get(url + '?q=jakarta&limit=1')
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_validation_get_cost_from_courier(self,client):
        url = self.prefix + '/get-cost'
        # field required
        response = client.post(url,json={})
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'origin': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'originType': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'destination': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'destinationType': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'weight': assert x['msg'] == 'field required'
            if x['loc'][-1] == 'courier': assert x['msg'] == 'field required'
        # all field blank
        response = client.post(url,json={
            'origin': 0,
            'originType': '',
            'destination': 0,
            'destinationType': '',
            'weight': 0,
            'courier': ''
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'origin': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'originType': assert x['msg'] == 'ensure this value has at least 3 characters'
            if x['loc'][-1] == 'destination': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'destinationType': assert x['msg'] == 'ensure this value has at least 3 characters'
            if x['loc'][-1] == 'weight': assert x['msg'] == 'ensure this value is greater than 0'
            if x['loc'][-1] == 'courier': assert x['msg'] == 'ensure this value has at least 3 characters'
        # test limit value
        response = client.post(url,json={
            'origin': 200,
            'originType': 'a' * 200,
            'destination': 200,
            'destinationType': 'a' * 200,
            'weight': 200,
            'courier': 'a' * 200
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'originType': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'destinationType': assert x['msg'] == 'ensure this value has at most 100 characters'
            if x['loc'][-1] == 'courier': assert x['msg'] == 'ensure this value has at most 100 characters'
        # check all field type data
        response = client.post(url,json={
            'origin': '123',
            'originType': 123,
            'destination': '123',
            'destinationType': 123,
            'weight': '123',
            'courier': 123
        })
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'origin': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'originType': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'destination': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'destinationType': assert x['msg'] == 'str type expected'
            if x['loc'][-1] == 'weight': assert x['msg'] == 'value is not a valid integer'
            if x['loc'][-1] == 'courier': assert x['msg'] == 'str type expected'

        # bad request from rajaongkir
        response = client.post(url,json={
            'origin': 2,
            'originType': 'citys',
            'destination': 3,
            'destinationType': 'subdistrict',
            'weight': 1000,
            'courier': 'jne'
        })
        assert response.status_code == 400
        assert response.json() == {'detail': "Bad request. originType yang valid adalah 'city' dan 'subdistrict'"}
        # internal server error from rajaongkir
        response = client.post(url,json={
            'origin': 900000,
            'originType': 'city',
            'destination': 3,
            'destinationType': 'subdistrict',
            'weight': 1000,
            'courier': 'jne'
        })
        assert response.status_code == 500
        assert response.json() == {"detail": "Failed to make a request to rajaongkir."}

    def test_get_cost_from_courier(self,client):
        url = self.prefix + '/get-cost'

        response = client.post(url,json={
            'origin': 2,
            'originType': 'city',
            'destination': 3,
            'destinationType': 'subdistrict',
            'weight': 1000,
            'courier': 'jne'
        })
        assert response.status_code == 200
        assert 'origin_detail' in response.json()
        assert 'destination_detail' in response.json()
        assert 'min_cost' in response.json()
        assert 'max_cost' in response.json()
        assert response.json()['costs_shipping'] != []
