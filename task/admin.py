from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
	list_filter = ('created_at', 'created_by')
	search_fields = ('title', 'description')
	list_display = ['title']

	class Meta:
		model = Task
	
admin.site.register(Task, TaskAdmin)