from django.conf.urls import url,include
from rbac.views import account

urlpatterns = [
    # 用户注册url
    url(r'^register/', account.Register.as_view(), name="register"),
    # 用户登录url
    url(r'^login/', account.Login.as_view(), name="login"),
    # 验证码url
    url(r'^get_auth_img/', account.GetAuthImg.as_view(), name="get_auth_img"),
]
