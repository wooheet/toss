from conftest import AuthAPITestCase


class TestAuthUserAPI(AuthAPITestCase):
    """
        로그인 사용자 API
    """

    def setUp(self):
        super().setUp()

    def test_auth(self):
        profile_data = {
            'date_of_birth': '1987-01-13'
        }
        print(profile_data)

