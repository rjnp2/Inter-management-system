from rest_framework import serializers
from .models import Attendance
from authentication.serializers import UserSerializer
from django.core.exceptions import NON_FIELD_ERRORS

class AttendanceSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ['user','entry_time', 'date_time','status','date_time','leave_reason']

    def get_user(self,obj):
        if obj.user:
            return obj.user.fullname()

class AttendanceSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ['entry_time','leave_time','date_time']

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "You have already take attendance for today.",
            }
        }

    def validate(self, attrs):
        if attrs['status'] == "present":
            if attrs['leave_reason']:
                raise serializers.ValidationError('leave reasons is not given when status is present.')
        return attrs
