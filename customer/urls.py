from django.conf.urls import url
from customer.views import customer

urlpatterns = [
    # 公户数据展示url
    url(r'^common/list', customer.CommonList.as_view(), name="common_list"),
    # 公户信息添加url
    url(r'^common/add/', customer.CommonAdd.as_view(), name="common_add"),
    # 公户信息修改url
    url(r'^common/edit/(\d+)/', customer.CommonEdit.as_view(), name="common_edit"),
    # 公户信息删除
    url(r'^common/del/(\d+)/', customer.CommonDel.as_view(), name="common_del"),

    # 私户数据展示
    url(r'^private/list/', customer.PrivateList.as_view(), name="private_list"),


]