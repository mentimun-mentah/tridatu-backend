class TestAddress:
    prefix = "/address"

    def test_search_city_or_district(self,client):
        url = self.prefix + "/search/city-or-district"

        # field required
        response = client.get(url)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'field required'
        # all field blank
        response = client.get(url + '?q=')
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at least 3 characters'
        # test limit value
        response = client.get(url + '?q=' + 'a' * 200)
        assert response.status_code == 422
        for x in response.json()['detail']:
            if x['loc'][-1] == 'q': assert x['msg'] == 'ensure this value has at most 100 characters'

        response = client.get(url + '?q=denpasar')
        assert response.status_code == 200
        assert len(response.json()) == 4
