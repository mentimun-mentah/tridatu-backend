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
