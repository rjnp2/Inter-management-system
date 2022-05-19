from rest_framework import serializers
from .models import Task
from authentication.serializers import ProfileOnlySerializer
      
class TaskSerializer(serializers.ModelSerializer):
	class Meta:
		model = Task
		fields = '__all__'
		read_only_fields= ('created_at','status')

	def validate(self, attrs):
		if attrs.get('assign_to'):
			for i in attrs.get('assign_to'):
				if i.role == 2:
					raise serializers.ValidationError(f'Only intern should add to assigned. {i} isnot interns.')

		return super().validate(attrs)

class TaskSerializerlist(serializers.ModelSerializer):
	created_by = serializers.SerializerMethodField()
	assign_to = serializers.SerializerMethodField()

	class Meta:
		model = Task
		fields ='__all__'

	def get_created_by(self,obj):
		return obj.created_by.user.fullname()
	
	def get_assign_to(self,obj):
		return [ o.user.fullname() for o in obj.assign_to.get_queryset()]