from django import forms
from education import models


class StudentStudyRecordMF(forms.ModelForm):
    class Meta:
        model = models.StudentStudyRecord  # 指定一个表
        # fields = '__all__'
        fields = ['score','homework_note']  # 只验证两个字段，其他字段放行