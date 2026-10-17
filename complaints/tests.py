from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from complaints.models import Complaint
from complaints.services import update_complaint_status

User = get_user_model()


class ComplaintServiceTests(TestCase):
	def setUp(self):
		self.member = User.objects.create_user(
			mobile_number='01900000001', full_name='Member', password='pass12345', is_active_member=True
		)
		self.manager = User.objects.create_user(
			mobile_number='01900000002', full_name='Manager', password='pass12345', is_active_member=True
		)

	def test_resolving_complaint_records_handler_and_time(self):
		complaint = Complaint.objects.create(
			raised_by=self.member, title='Water', description='No water in the kitchen.'
		)
		update_complaint_status(complaint, Complaint.STATUS_RESOLVED, self.manager)

		complaint.refresh_from_db()
		self.assertEqual(complaint.handled_by, self.manager)
		self.assertIsNotNone(complaint.resolved_at)


class ComplaintAPITests(APITestCase):
	def setUp(self):
		self.member = User.objects.create_user(
			mobile_number='01900000003', full_name='Member', password='pass12345', is_active_member=True
		)
		self.other_member = User.objects.create_user(
			mobile_number='01900000004', full_name='Other', password='pass12345', is_active_member=True
		)

	def test_member_can_create_and_only_see_own_complaints(self):
		self.client.force_authenticate(self.member)
		create_response = self.client.post('/api/complaints/', {
			'title': 'Light', 'description': 'The light is broken.'
		})
		Complaint.objects.create(
			raised_by=self.other_member, title='Other', description='Private complaint.'
		)
		list_response = self.client.get('/api/complaints/my-complaints/')

		self.assertEqual(create_response.status_code, 201)
		self.assertEqual(list_response.status_code, 200)
		self.assertEqual(len(list_response.data), 1)
