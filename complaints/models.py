from django.conf import settings
from django.db import models


class Complaint(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_IN_PROGRESS = 'in_progress'
	STATUS_RESOLVED = 'resolved'
	STATUS_CHOICES = (
		(STATUS_PENDING, 'Pending'),
		(STATUS_IN_PROGRESS, 'In Progress'),
		(STATUS_RESOLVED, 'Resolved'),
	)

	raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title = models.CharField(max_length=150)
	description = models.TextField()
	status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
	handled_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='handled_complaints',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	resolved_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.title
