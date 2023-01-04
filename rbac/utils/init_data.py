import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ObCRM.settings")  # 引入django的环境
    import django
    django.setup()
    from rbac import models


    # 初始化用户数据
    # models.UserInfo.objects.create_superuser(
    #     username = "ryxiong",
    #     password = "ryxiong520",
    #     gender=1,
    #     phone="17788979651",
    #     email="275310126@qq.com",
    # )
    # models.UserInfo.objects.create_user(
    #     username="alex",
    #     password="alex123",
    #     gender=1,
    #     phone="1245638792",
    #     email="alex@qq.com",
    # )
    # models.UserInfo.objects.create_user(
    #     username="chao",
    #     password="chao123",
    #     gender=2,
    #     phone="14236587952",
    #     email="chao@163.com",
    # )
    # models.UserInfo.objects.create_user(
    #     username="jinjin",
    #     password="jinjin123",
    #     gender=2,
    #     phone="1475869231",
    #     email="jinjin@qq.com",
    # )
    # models.UserInfo.objects.create_user(
    #     username="baozhu",
    #     password="baozhu123",
    #     gender=2,
    #     phone="1385454667",
    #     email="baozhu@qq.com",
    # )