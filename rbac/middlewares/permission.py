import re
from rbac import models
from django.shortcuts import HttpResponse,redirect,render
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class PermissionMiddleware(MiddlewareMixin):
    """自定义权限分配中间件"""
    def process_request(self,request):
        # 对权限进行校验
        # 1. 当前访问的URL在不在白名单
        for i in settings.WHITE_URL_LIST:
            ret = re.search(i,request.path)
            if ret:
                return None

        # 获取当前用户的所有权限
        user = request.user
        if not user:
            return redirect("login")

        # 创建面包屑数据（路径导航）
        request.breadcrumb = [
            # {"title":"主页","url":"/crmweb/index/"}
        ]

        # 获取用户权限列表
        permissions_list = request.session.get("permissions_list")
        if permissions_list:
            for permission in permissions_list:  # 遍历权限列表，匹配当前路径，匹配上放行
                url = permission['url']
                if re.search(f"^{url}",request.path):
                    # 请求子权限路径，父级权限和父级菜单激活样式设置
                    request.show_id = permission["parent_id"]
                    # # 添加面包屑展示路径
                    # # 1.添加一层
                    # if not permission["parent_id"]:
                    #     if permission["url"]:
                    #         request.breadcrumb.append({"name": permission["name"], "url": "javascript:void(0)"})
                    # # 2.添加多层
                    # else:
                    #     parent = models.Permission.objects.filter(pk=permission["parent_id"]).first()
                    #     # 2.1 添加二层
                    #     if not parent.parent_id:
                    #         if not parent.url:
                    #             parent.url = "javascript:void(0)"
                    #         request.breadcrumb.append({"name": parent.name, "url": parent.url})
                    #         request.breadcrumb.append({"name": permission["name"], "url": permission["url"]})
                    #     # 2.2 添加三层
                    #     else:
                    #         grandparent = models.Permission.objects.filter(pk=parent.parent_id).first()
                    #         if not grandparent.url:
                    #             grandparent.url = "javascript:void(0)"
                    #         request.breadcrumb.append({"name": grandparent.name, "url": grandparent.url})
                    #         request.breadcrumb.append({"name": parent.name, "url": parent.url})
                    #         request.breadcrumb.append({"name": permission["name"], "url": permission["url"]})

                    return None

        # 没有匹配上，提示没有权限
        return HttpResponse("没有权限")