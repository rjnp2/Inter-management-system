from django.contrib import admin
from .models import Attendance

# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user','date_time','status','entry_time',
                    'leave_time']
                    
    list_display_links = list_display
    readonly_fields = ['user','date_time','status','entry_time']
    ordering = ('-date_time',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Attendance, AttendanceAdmin)