from django.db import models
from multiselectfield import MultiSelectField
# 安装:pip install django-multiselectfield,针对choices多选用的

# Create your models here.


# 客户来源分类
source_type = (('qq', "qq群"),
               ('referral', "内部转介绍"),
               ('website', "官方网站"),
               ('baidu_ads', "百度推广"),
               ('office_direct', "直接上门"),
               ('WoM', "口碑"),
               ('public_class', "公开课"),
               ('website_luffy', "路飞官网"),
               ('others', "其它"),)

# 报名状态分类
enroll_status_choices = (('signed', "已报名"),
                         ('unregistered', "未报名"),
                         ('studying', '学习中'),
                         ('paid_in_full', "学费已交齐"))

# 客户意向分类
seek_status_choices = (
    ('A', '近期无报名计划'),
    ('B', '1个月内报名'),
    ('C', '2周内报名'),
    ('D', '1周内报名'),
    ('E', '定金'),
    ('F', '到班'),
    ('G', '全款'),
    ('H', '无效'),
)

# 咨询班级类型
class_type_choices = (('fulltime', '脱产班',),
                      ('online', '网络班'),
                      ('weekend', '周末班',),)

# 咨询课程选择
course_choices = (
    ('Linux', 'Linux高级'),
    ('PythonFullStack', 'Python高级全栈开发'),
    ('BigData', '大数据开发'),
)


# 客户信息表
class Customer(models.Model):
    """
    客户表（最开始的时候大家都是客户，销售就不停的撩你，你还没交钱就是个客户）
    """
    qq = models.CharField(verbose_name='QQ', max_length=64, unique=True, help_text='QQ号必须唯一')
    qq_name = models.CharField('QQ昵称', max_length=64, blank=True, null=True)
    name = models.CharField('姓名', default="潜在客户", max_length=32, blank=True, null=True, help_text='学员报名后，请改为真实姓名')
    gender_type = (('male', '男'), ('female', '女'))
    gender = models.CharField("性别", choices=gender_type, max_length=16, default='male', blank=True,
                              null=True)  # 存的是male或者female，字符串

    birthday = models.DateField('出生日期', default=None, help_text="格式yyyy-mm-dd", blank=True, null=True)

    phone = models.CharField('手机号', blank=True, null=True, max_length=32)
    # phone = models.CharField('手机号', blank=True, null=True)
    source = models.CharField('客户来源', max_length=64, choices=source_type, default='qq')
    introduce_from = models.ForeignKey('self', verbose_name="转介绍自学员", blank=True,
                                       null=True)  # self指的就是自己这个表，和下面写法是一样的效果

    # introduce_from = models.ForeignKey('Customer', verbose_name="转介绍自学员", blank=True, null=True,on_delete=models.CASCADE)
    course = MultiSelectField("咨询课程", choices=course_choices, blank=True, null=True)  # 多选，并且存成一个列表的格式
    # course = models.CharField("咨询课程", choices=course_choices) #如果你不想用上面的多选功能，可以使用Charfield来存
    class_type = models.CharField("咨询班级类型", max_length=64, choices=class_type_choices, default='fulltime', blank=True,
                                  null=True)
    customer_note = models.TextField("客户备注", blank=True, null=True, )
    status = models.CharField("状态", choices=enroll_status_choices, max_length=64, default="unregistered",
                              help_text="选择客户此时的状态")  # help_text这种参数基本都是针对admin应用里面用的

    date = models.DateTimeField("咨询日期", )

    last_consult_date = models.DateField("最后跟进日期", auto_now_add=True)  # 考核销售的跟进情况，如果多天没有跟进，会影响销售的绩效等

    next_date = models.DateField("预计再次跟进时间", blank=True, null=True)  # 销售自己大概记录一下自己下一次会什么时候跟进，也没啥用

    # 用户表中存放的是自己公司的所有员工。
    consultant = models.ForeignKey('rbac.UserInfo', verbose_name="销售", blank=True, null=True)

    def __str__(self):
        return self.qq_name  # 主要__str__最好是个字符串昂，不然你会遇到很多的坑，还有我们返回的这两个字段填写数据的时候必须写上数据，必然相加会报错，null类型和str类型不能相加等错误信息。


# 跟进记录表
class ConsultRecord(models.Model):
    """
    跟进记录表
    """
    customer = models.ForeignKey('Customer', verbose_name="咨询客户")

    status = models.CharField("跟进状态", max_length=8, choices=seek_status_choices, help_text="选择客户此时的状态")

    note = models.TextField(verbose_name="跟进内容...")

    consultant = models.ForeignKey("rbac.UserInfo", verbose_name="跟进人", related_name='records')

    date = models.DateTimeField("跟进日期", auto_now_add=True)

    delete_status = models.BooleanField(verbose_name='删除状态', default=False)


# 登记报名表
class Enrollment(models.Model):
    """报名表"""
    customer = models.ForeignKey('Customer', verbose_name='客户名称')

    why = models.TextField("为什么报名", max_length=1024, default=None, blank=True, null=True)

    expectation = models.TextField("学习期望", max_length=1024, blank=True, null=True)

    enrolled_date = models.DateTimeField(verbose_name="报名日期")

    memo = models.TextField('备注', blank=True, null=True)

    delete_status = models.BooleanField(verbose_name='删除状态', default=False)

    school = models.ForeignKey('education.Campuses')  # 校区表

    enrollment_class = models.ForeignKey("education.ClassList", verbose_name="所报班级")

    class Meta:
        unique_together = ('enrollment_class', 'customer')
