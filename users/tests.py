# from django.test import TestCase
# from django.urls import reverse
# from config.conftest import AuthAPITestCase
#
#
# class TestAuthorizedtUserAPI(AuthAPITestCase):
#     """
#         로그인 사용자 API Call Test
#     """
#
#     def test_profile_date_of_birth_update_before_auth(self):
#         profile_data = {
#             'date_of_birth': '1987-01-13'
#         }
#         my_id = self.user.get('id')
#
#         res = self.client.put(
#             reverse('user-detail', kwargs={'pk': my_id}),
#             data=profile_data,
#             format='json'
#         )
#         results = res.data.get('results')[0]
#         self.assertEqual(res.status_code, 200)
#         self.assertEqual(
#             results.get('date_of_birth').strftime('%Y-%m-%d'), '1987-01-13')
