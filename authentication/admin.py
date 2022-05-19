from django.contrib import admin
from .models import Profile,User

# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = 'user'

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email','first_name','last_name','last_login',
                    'is_staff','is_active']
                    
    list_display_links = ('email',)
    readonly_fields = ('last_login','created_at')
    ordering = ('-created_at',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.register(User, CustomUserAdmin)