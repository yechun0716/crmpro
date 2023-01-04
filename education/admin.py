from django.contrib import admin
from education import models

# Register your models here.

class StuStudyRecordAdmin(admin.ModelAdmin):
    list_display = ["student","class_study_record","record","score"]
    list_editable = ["record","score"]


admin.site.register(models.Student)
admin.site.register(models.ClassStudyRecord)
admin.site.register(models.StudentStudyRecord,StuStudyRecordAdmin)
