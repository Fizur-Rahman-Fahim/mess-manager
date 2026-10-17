from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class SettingsAndManagerAPITests(APITestCase):
	def setUp(self):
		self.super_manager = User.objects.create_superuser(
			mobile_number='01800000001',
			full_name='Super Manager',
			password='pass12345',
		)
		self.member = User.objects.create_user(
			mobile_number='01800000002',
			full_name='Member',
			password='pass12345',
			is_active_member=True,
		)

	def test_member_can_read_settings_but_cannot_update(self):
		self.client.force_authenticate(self.member)
		read_response = self.client.get('/api/settings/')
		update_response = self.client.patch('/api/settings/', {'seat_bill_default': '1200.00'})

		self.assertEqual(read_response.status_code, 200)
		self.assertEqual(update_response.status_code, 403)

	def test_super_manager_can_update_settings(self):
		self.client.force_authenticate(self.super_manager)
		response = self.client.patch('/api/settings/', {
			'seat_bill_default': '1200.00',
			'breakfast_meal_value': '0.75',
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['seat_bill_default'], '1200.00')
		self.assertEqual(response.data['updated_by'], self.super_manager.id)

	def test_token_refresh_returns_new_access_token(self):
		login_response = self.client.post(
			'/api/auth/login/',
			{'mobile_number': '01800000001', 'password': 'pass12345'},
			format='json',
		)
		self.assertEqual(login_response.status_code, 200)
		refresh = login_response.data['refresh']

		refresh_response = self.client.post(
			'/api/auth/refresh/',
			{'refresh': refresh},
			format='json',
		)
		self.assertEqual(refresh_response.status_code, 200)
		self.assertIn('access', refresh_response.data)

	def test_inactive_member_cannot_access_member_api(self):
		inactive = User.objects.create_user(
			mobile_number='01800000003', full_name='Inactive', password='pass12345'
		)
		self.client.force_authenticate(inactive)
		response = self.client.get('/api/settings/')
		self.assertEqual(response.status_code, 403)

# Create your tests here.
