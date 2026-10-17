from rest_framework import serializers

from complaints.models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    raised_by_name = serializers.CharField(source='raised_by.full_name', read_only=True)
    handled_by_name = serializers.CharField(source='handled_by.full_name', read_only=True)

    class Meta:
        model = Complaint
        fields = (
            'id', 'raised_by', 'raised_by_name', 'title', 'description', 'status',
            'handled_by', 'handled_by_name', 'created_at', 'resolved_at',
        )
        read_only_fields = ('raised_by', 'handled_by', 'created_at', 'resolved_at')


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('title', 'description')


class ComplaintStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Complaint.STATUS_CHOICES)
