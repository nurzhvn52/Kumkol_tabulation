from django.contrib import admin
from .models import *
from .forms import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
# Register your models here.

class TabelAdmin(ImportExportModelAdmin):
    # list_display = ('id', 'name', 'tabel_number', 'job', 'Category', "value_1", "value_2", "value_3", "value_4", "value_5", 'value_6', 'value_7', 'value_8', 'value_9', 'value_10', 'value_11', 'value_12', 'value_13', 'value_14', 'value_15', 'value_16', 'value_17', 'value_18', 'value_19', 'value_20', 'value_21', 'value_22', 'value_23', 'value_24', 'value_25', 'value_26', 'value_27', 'value_28', 'value_29', 'value_30', 'value_31', "attendance_days", "K_ch", "K", 'KO_ch', 'K_k', 'CP_ch', 'vacation', 'decree', 'disability', 'study_vacation', 'excused', 'absense', 'excused_admin', 'D', 'N', 'T', 'X', 'vacition_salary', 'Pr', 'time_off', 'weekends_off', "month_days", 'total_work_hour', 'renovation', 'holidays', 'weekends', 'night_shift', 'overtime', 'surcharge_procents', 'hours_in_unhealthy', 'unworked_simple', 'baby_feeding_breaks', 'meal_breaks')
    list_display = ('id', 'name', 'tabel_number', 'job', 'Category', "attendance_days",'total_work_hour')

class TabelAdmin(admin.ModelAdmin):
    list_display = ('id','reservoir','subdivision','year')
    list_filter = ('year','reservoir','subdivision')


admin.site.register(Employees)
admin.site.register(Job)
admin.site.register(Subdivision)
admin.site.register(OilPlace)
admin.site.register(Attendance)
admin.site.register(TimeTracking)
admin.site.register(WorkedTime)
admin.site.register(Tabel,TabelAdmin)
admin.site.login_form = AdminUsernameAuthenticationForm
class AccountAdmin(UserAdmin):
    list_display = ('email', 'date_joined', 'last_login', 'is_staff', )
    search_fields = ('email', )
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
            (
                None,
                {
                    'classes': ('wide',),
                    'fields': ('email','first_name', 'last_name','is_staff','is_superuser' ,'password1', 'password2'),
                },
            ),
        )
    
    def save_model(self, request, obj, form, change):
        if not obj.username:
            email_parts = obj.email.split('@')
            username = f"{email_parts[0]}"  
            obj.username = username

        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, AccountAdmin)
