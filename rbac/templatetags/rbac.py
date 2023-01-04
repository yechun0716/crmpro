import re
from django import template

register = template.Library()


@register.inclusion_tag("menu.html")
def get_menu(request):
    menus_dict = request.session.get("menus_dict")
    for menu in menus_dict.values():  # 遍历菜单
        for child in menu.get("children"):  # 遍历子菜单的children列表
            if re.match(child["url"],request.path) or request.show_id == child["pk"]:  # 对当前路径进行匹配，匹配上了给二级菜单加上激活样式，同时给父级菜单也加上激活样式,或者当前路径是某个二级菜单权限的子权限
                menu["class"] = "active"
                child["class"] = "active"
    return {"menus_dict": menus_dict}
