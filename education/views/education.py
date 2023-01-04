from django import views
from django.http import JsonResponse
from django.shortcuts import (
    render, redirect, reverse, HttpResponse
)
from education import models
from education.forms.formauth import StudentStudyRecordMF
from django.forms.models import modelformset_factory
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


# 班级学习记录视图
class ClassStudyRecord(views.View):
    @method_decorator(login_required)  # 校验用户登录
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request,*args,**kwargs)
        return res

    def get(self,request):
        # 获取所有班级的课程记录
        all_records = models.ClassStudyRecord.objects.all()
        return render(request, "class_record_list.html", {"all_records":all_records})

    def post(self,request):
        # 获取批量操作类型
        operate = request.POST.get("operate")
        # 获取批量提交的班级课程记录id
        selected_id = request.POST.getlist("choose")
        print(operate)
        if hasattr(self,operate):  # 反射类中的批量操作方法
            getattr(self,operate)(selected_id)
        return self.get(request)

    def batch_create(self,selected_id):
        for class_record_id in selected_id:
            # 根据班级课程记录查到多有的学生对象.
            # 注意班级和学生，一对多关联，通过班级反向找学生，类名小写_set.all()，但是外键字段取了related_name，所以直接使用别名students.all()
            all_students = models.ClassStudyRecord.objects.get(pk=class_record_id).class_obj.students.all()
            # print(all_students)
            # 给所有学生创建一条学习记录，只填好学生姓名，和所属的哪一节课程.
            li = []
            for student in all_students:
                # 根据每一个学生实例化一个学生学习记录对象
                student_record = models.StudentStudyRecord(
                    student=student,
                    class_study_record_id=class_record_id
                )
                li.append(student_record)
            # 批量创建记录
            models.StudentStudyRecord.objects.bulk_create(li)


# 学生学习记录视图,普通的
class StudentStudyRecord(views.View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        ret = super().dispatch(request,*args,**kwargs)
        return ret

    def get(self,request,class_record_id=None):
        if class_record_id:  # 有班级id，说明是批量修改请求
            # 通过modelformset批量修改
            ret = self.batch_edit_mfs(request,class_record_id)
        else:
            # 没有是数据展示请求
            ret = self.display(request)
        return ret

    def display(self,request):
        """
        直接请求学生学习记录展示的页面
        :param request:
        :return:
        """
        # 找到这节班级课程的所有学生学习记录
        all_records = models.StudentStudyRecord.objects.all()

        # 获取分数的可选选项
        score_choices = models.score_choices

        return render(request, "student_record_list.html",{"all_records": all_records,"score_choices": score_choices})

    """批量修改展示数据的两种方式"""
    # 第一种方式，通过手动遍历数据展示批量修改的数据列表
    def batch_edit(self,request,class_record_id):
        # 通过班级记录id，找到班级课程的那一条记录
        class_record_obj = models.ClassStudyRecord.objects.get(pk=class_record_id)

        # 通过班级对象，找到这节班级课程的所有学生学习记录
        all_records = models.StudentStudyRecord.objects.filter(class_study_record=class_record_obj)

        # 获取分数的可选选项
        score_choices = models.score_choices

        return render(request,"student_record_edit.html",{"class_record_obj":class_record_obj,"all_records":all_records,"score_choices":score_choices})

    # 第二种方式，通过使用modelformset来生成批量修改的页面
    def batch_edit_mfs(self,request,class_record_id):
        # 通过班级记录id，找到班级课程的那一条记录
        class_record_obj = models.ClassStudyRecord.objects.get(pk=class_record_id)

        # 通过班级对象，找到这节班级课程的所有学生学习记录
        all_records = models.StudentStudyRecord.objects.filter(
            class_study_record=class_record_obj,
        )

        # 实例化一个form_set对象
        form_set_obj = modelformset_factory(
            model=models.StudentStudyRecord,  # 指定一张表
            form=StudentStudyRecordMF,  # 指定一个modelform
            extra=0  # 可以指定生成表中，新建数据的行数，看页面效果就理解了
        )

        # 将所有的学生学习记录传给form_set对象的queryset
        all_records = form_set_obj(queryset=all_records)

        return render(request,"student_record_edit.html",{"class_record_obj":class_record_obj,"all_records":all_records})

    """批量提交修改数据的两种方式"""
    def post(self,request,class_record_id=None):
        # 调用不同的方式来批量修改数据
        self.batch_commit_mfs(request,class_record_id)

        return self.get(request,class_record_id)

    # 第一种方式，通过手动获取数据，提取数据结构来更新数据
    def batch_commit(self,request,class_record_id):
        data = request.POST
        # print(data)  # <QueryDict: {'csrfmiddlewaretoken': ['R73Lgac0jPy6YwP1guZ4fC5wLsrVY4iGgd45hip6xtcxZNfuiysmRwGt2IZhi0K0'], 'socre_1': ['80'], 'homework_note_1': ['请问'], 'socre_4': ['90'], 'homework_note_4': ['武器二人'], 'socre_5': ['100'], 'homework_note_5': ['未确认']}>

        # 构件我们想要的数据类型
        """
        {
            1:{"score":80,"homework_note":"123"},
            2:{"score":85,"homework_note":"456"},
        }
        """
        cleaned_data = {}
        for key,val in data.items():
            if key == "csrfmiddlewaretoken":continue
            field,pk = key.rsplit("_",1)
            if pk in cleaned_data:
                cleaned_data[pk].update({field:val})
            else:
                cleaned_data[pk] = {field:val}

        for pk,val in cleaned_data.items():
            models.StudentStudyRecord.objects.filter(pk=pk).update(**val)

    # 第二种方式，通过modelformset提供的save方法存储
    def batch_commit_mfs(self,request,class_record_id):
        # 通过班级记录id，找到班级课程的那一条记录
        class_record_obj = models.ClassStudyRecord.objects.get(pk=class_record_id)

        # 实例化一个form_set对象
        form_set_obj = modelformset_factory(
            model=models.StudentStudyRecord,  # 指定一张表
            form=StudentStudyRecordMF,  # 指定一个modelform
            extra=0  # 可以指定生成表中，新建数据的行数，看页面效果就理解了
        )
        print(request.POST)

        # 将提交的form数据传给form_set对象
        all_records = form_set_obj(request.POST)
        print(all_records)

        if all_records.is_valid():  # 对提交的数据进行验证
            all_records.save()  # 如果合法，则保存导数据
        else:  # 如果不合法，将错误的提示重新渲染到页面，
            print(all_records.errors)