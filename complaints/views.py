from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View

from complaints.forms import ComplaintForm
from complaints.models import Complaint
from complaints.services import update_complaint_status
from expenses.mixins import ManagerRequiredMixin


class MyComplaintsView(LoginRequiredMixin, ListView):
	template_name = 'complaints/my_complaints.html'
	context_object_name = 'complaints'

	def get_queryset(self):
		return Complaint.objects.filter(raised_by=self.request.user)


class ComplaintCreateView(LoginRequiredMixin, CreateView):
	template_name = 'complaints/form.html'
	form_class = ComplaintForm
	success_url = reverse_lazy('complaints:my_complaints')

	def form_valid(self, form):
		form.instance.raised_by = self.request.user
		messages.success(self.request, 'Complaint submitted.')
		return super().form_valid(form)


class AllComplaintsView(ManagerRequiredMixin, ListView):
	template_name = 'complaints/all.html'
	context_object_name = 'complaints'
	queryset = Complaint.objects.select_related('raised_by', 'handled_by').all()


class ComplaintStatusView(ManagerRequiredMixin, View):
	def post(self, request, complaint_id):
		complaint = get_object_or_404(Complaint, pk=complaint_id)
		next_status = request.POST.get('status', '')
		try:
			update_complaint_status(complaint, next_status, request.user)
		except ValidationError as exc:
			messages.error(request, str(exc))
		else:
			messages.success(request, 'Complaint status updated.')
		return redirect('complaints:all')
