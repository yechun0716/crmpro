from education.views import education
from django.conf.urls import url

urlpatterns = [
    # 班级课程记录展示
    url(r'^class/record/list/', education.ClassStudyRecord.as_view(), name="class_record"),

    # 学员学习记录展示
    url(r'^student/record/list/(\d+)?/?', education.StudentStudyRecord.as_view(), name="student_record"),
]