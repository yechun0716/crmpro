from django import views
from customer import models
from django.db.models import Q, Count
from django.shortcuts import (
    render, redirect, reverse, HttpResponse
)
from customer.forms import formAuth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from utils.customPaginator import Paginator

# 主页
class Index(views.View):
    @method_decorator(login_required)  # 装饰器函数验证是否登录
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        return res
    def get(self,request):
        # 展示主页
        return render(request,"index.html")


# 公户数据展示
class CommonList(views.View):
    @method_decorator(login_required)  # 装饰器函数验证是否登录
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        return res

    def get(self, request):
        # 查询公户全部数据
        all_customers = models.Customer.objects.filter(consultant__isnull=True, status="unregistered").order_by(
            "-pk")

        # 使用Q查询拼接查询条件
        condition = request.GET.get("condition", "")  # 获取搜索的条件分类
        query = request.GET.get("q", "")  # 获取搜索的条件
        if condition and query:  # 如果有查询调参数，两个参数都有，根据查询参数查询后找到数据
            condition = condition + "__contains"
            q = Q()  # Q实例化生成q对象，q对象可以帮我们拼接字符串为 condition__contians= xx的关键字参数传到filter中。
            q.children.append((condition, query))
            all_customers = all_customers.filter(q)

        # 开始分页展示
        data_counts = all_customers.count()  # 获取分页的总数据数量

        # 生成一个分页对象
        paginator = Paginator(request, data_counts, 10)

        # 获取当前页展示数据的范围
        try:  # 异常是否查到了数据，查到了才切片，不然会报错
            all_customers = all_customers[paginator.start:paginator.end]
        except Exception:
            pass

        # 获取分页的标签
        paginator_tag = paginator.paginate()  # 调用定义好的分页方法

        # 获取跳转页的标签
        jump_tag = paginator.jump_page()  # 调用定义好的跳转页方法获取跳转页标签
        jump_js = paginator.jump_js()  # 调用定义好的跳转页方法获取跳转页js代码

        # fixme 这里我实现的用户被选走的提示方式有点low，暂时先这样吧，而且在实际业务中，公户转私户应该是由销售总监分配的，而不是比谁先抢到。
        name_str = None
        # 客户被选走的错误提示
        if "*customer*" in request.path:
            name_list = request.path.split("*customer*")[1:]
            name_str = ','.join(name_list)

        # 返回response对象，以及需要渲染的数据
        return render(request, "common_list.html",{"all_customers": all_customers, "paginator_tag": paginator_tag,"jump_tag": jump_tag, "jump_js": jump_js, "name_str": name_str})

    def post(self, request):
        operate = request.POST.get("operate")  # 获取用户提交的批量操作类型
        if operate:
            # 如果有，去反射类中对应的批量操作方法
            if hasattr(self, operate):
                func = getattr(self, operate)
                if callable(func):
                    ret = func(request)  # 执行批量操作方法
                    if ret:  # 函数有返回值，也就是有被别的销售提前选走的客户
                        info = ""
                        for obj in ret:
                            # fixme 客户被任选走，在前端提示哪些客户被选走，这里我放在路径中，并不太好，目前就这样实现，以后有更好的办法再更新
                            info = info + "*customer*" + obj.__str__()
                        url = request.path + info  # 拼接url，携带提示信息
                        return redirect(url)
                    return redirect(request.path)
                else:
                    return HttpResponse("访问连接有误！")
            return HttpResponse("访问连接有误！")
        return redirect("common")

    def batch_delete(self, request, *args, **kwargs):
        """批量删除客户"""
        # 实际工作场景中并不是真的删除，而是修改该条数据在数据库的修改状态
        choose_list = request.POST.getlist("choose")
        models.Customer.objects.filter(pk__in=choose_list).delete()

    def batch_update(self, request, *args, **kwargs):
        """批量更新客户状态"""
        choose_list = request.POST.getlist("choose")
        models.Customer.objects.filter(pk__in=choose_list).update(status="studying")

    def batch_c2p(self, request, *args, **kwargs):
        """批量公户转私户操作"""
        choose_list = request.POST.getlist("choose")  # 获取选中的客户id，注意通过getlist来获取，获取一个列表
        customer_list = models.Customer.objects.filter(pk__in=choose_list)  # 根据客户id查到客户

        has_choosed = []  # 定义一个列表
        for customer_obj in customer_list:
            if customer_obj.consultant:  # 如果客户被别人选了，放到已选列表
                has_choosed.append(customer_obj)
            else:
                # 如果还没有备选则选择并保存
                customer_obj.consultant = request.user
                customer_obj.save()  # 通过save方法保存到数据库
        return has_choosed  # 返回已经被选择的用户


# 私户数据展示
class PrivateList(views.View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        return res

    def get(self, request):
        condition = request.GET.get("condition", "")
        query = request.GET.get("q", "")
        condition = condition + "__contains"
        q = Q()  # Q实例化生成q对象，q对象可以帮我们拼接字符串为 condition__contians= xx的关键字参数传到filter中。
        q.children.append((condition, query))

        if condition and query:  # 如果有查询调参数，两个参数都有，根据查询参数查询后找到数据
            all_customers = models.Customer.objects.filter(q, consultant=request.user).order_by("-pk")
        else:  # 判断有没有查询参数，只有有一个没有参数，就查询所有公户数据
            all_customers = models.Customer.objects.filter(consultant=request.user).order_by("-pk")

        # 开始分页展示
        data_counts = all_customers.count()

        # 生成一个分页对象
        paginator = Paginator(request, data_counts, 10)

        # 获取当前页展示数据的范围
        try:  # 异常是否查到了数据，查到了才切片，不然会报错
            all_customers = all_customers[paginator.start:paginator.end]
        except Exception:
            pass

        # 获取分页的标签
        paginator_tag = paginator.paginate()  # 调用定义好的分页方法

        # 获取跳转页的标签
        jump_tag = paginator.jump_page()  # 调用定义好的跳转页方法

        return render(request, "private_list.html",
                      {"all_customers": all_customers, "paginator_tag": paginator_tag, "jump_tag": jump_tag})


# 添加公共客户记录
class CommonAdd(views.View):
    """添加公户记录视图"""
    @method_decorator(login_required)  # 登录验证
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        return res

    def get(self, request):
        form_obj = formAuth.CustomerAddMF()  # 通过modelform实例化生成对象
        return render(request, "common_add.html", {"form_obj": form_obj})

    def post(self, request):
        # 实例化modelform并传入前端提交的数据
        form_obj = formAuth.CustomerAddMF(request.POST)
        if form_obj.is_valid():  # 对提交数据验证
            form_obj.save()  # 合法保存到数据库
            return redirect("common_list")
        else:
            # 不合法将原有数据返回给页面，并显示错误提示
            return render(request, "common_add.html", {"form_obj": form_obj})


# 修改公共客户记录
class CommonEdit(views.View):
    @method_decorator(login_required)  # 登录验证状态
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        return res

    def get(self, request, n):
        """
        get请求，展示修改页面，其中展示原始数据
        :param request: request请求
        :param n: 前端传递过来的记录id
        :return: 返回response对象
        """
        customer_obj = models.Customer.objects.filter(pk=n).first()  # 找到需要修改的客户对象
        form_obj = formAuth.CustomerAddMF(instance=customer_obj)  # 通过modelform实例化的instance参数指定一个客户对象，可以在前端页面中直接渲染原始数据。
        return render(request, "common_add.html", {"form_obj": form_obj})

    def post(self, request, n):
        """修改客户记录post请求"""
        customer_obj = models.Customer.objects.filter(pk=n).first()
        # 通过modelform实例化，传递页面提交的post数据，指定instance实例
        form_obj = formAuth.CustomerAddMF(request.POST, instance=customer_obj)
        if form_obj.is_valid():
            form_obj.save()  # 合法后保存，注意如果实例化时，没有传实例，是创建记录，指定了实例才是修改数据
            return redirect("common")

        else:
            # 数据不合法，保留页面和原始数据，并给出错误提示
            return render(request, "common_add.html", {"form_obj": form_obj})


# 删除公共客户记录
class CommonDel(views.View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        return res

    def get(self, request, n):
        customer_obj = models.Customer.objects.filter(pk=n)
        customer_obj.delete()  # fixme 对象的delete方法删除，其实实际工作中不应是真的删除，而是修改该记录的删除状态为True，即可。
        return redirect("common_list")