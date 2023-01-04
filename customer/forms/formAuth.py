from django import forms
from customer import models


# 顾客添加form认证
class CustomerAddMF(forms.ModelForm):
    # 定义添加数据使用的ModelForm
    class Meta:
        model = models.Customer  # 指定一张表
        fields = "__all__"  # 指定字段，排除用exclude

    def __init__(self,*args,**kwargs):
        """重写init方法，批量添加标签样式"""
        super().__init__(*args,**kwargs)  # 执行父类的init方法，必须
        for field in self.fields:
            if field != "course":  # 课程是多选框，不设置标签样式
                self.fields[field].widget.attrs.update({"class":"forms-control",})