import copy
class Paginator:
    """自定义分页器"""
    def __init__(self, request, data_counts, per_counts=10, show_counts=5):
        """
        初始属性
        :param request: 请求的所有请求数据
        :param data_counts: 展示的总数据数量
        :param per_counts: 每页展示的数据数量
        :param show_counts: 在前端显示的页码数量
        """
        self.request = request
        self.data_counts = data_counts
        self.per_counts = per_counts
        self.show_counts = show_counts
        self.params = copy.deepcopy(request.GET)  # 获取请求的GET数据的深拷贝querydict可以使用

        # 获取数据分页后总页数
        def page_counts():
            """
            获取总的页码数量
            :return:
            """
            page_counts, mod = divmod(self.data_counts, self.per_counts)
            if mod:
                page_counts += 1
            return page_counts

        # 获取总页数，并添加在self属性中
        self.page_counts = page_counts()

        # 获取当前页页码
        self.current_page = request.GET.get("page", "")

        try:  # 异常处理当前页码是否为数字
            self.current_page = int(self.current_page)
        except Exception:
            self.current_page = 1

        # 判断当前页码在不在合理范围内
        if self.current_page < 1:
            self.current_page = 1
        if self.current_page > self.page_counts:
            self.current_page = 1

    @property  # 装饰为普通属性
    def start(self):
        """
        返回某一页数据展示的开始位置
        :return:
        """
        return (self.current_page - 1) * self.per_counts

    @property  # 装饰为普通属性
    def end(self):
        """
        返回某一页数据展示的结束位置
        :return:
        """
        return (self.current_page) * self.per_counts

    def paginate(self):
        """
        根据数据数据量，每页数据，每页页码，拼接分页标签返回
        :return:返回拼接好的分页器标签
        """
        tag = ""
        page_counts = self.page_counts

        # 设置首页标签url
        self.params["page"] = 1
        params = self.params.urlencode()  # condition=name&q=qwerqw&page=1
        if self.current_page == 1:
            first = f"""
                <li class="active">
                    <a href="{self.request.path}?{params}" aria-label="Previous">
                        <span aria-hidden="true">首页</span>
                    </a>
                </li>
                """
        else:
            first = f"""
                <li>
                    <a href="{self.request.path}?{params}" aria-label="Previous">
                        <span aria-hidden="true">首页</span>
                    </a>
                </li>
                """

        # 设置上一页标签的url
        if self.current_page <= 1:
            # 如果当前页是第一页，上一页不可选
            previous = """
                <li disabled>
                    <a href="#" aria-label="Previous">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>
                """
        else:
            # 不是第一页，拼接上一页的url路径
            self.params["page"] = self.current_page - 1
            params = self.params.urlencode()  # condition=name&q=qwerqw&page=num
            previous = f"""
                <li>
                    <a href="{self.request.path}?{params}" aria-label="Previous">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>
                """

        # 获取要显示的页码范围
        half_num = self.show_counts // 2
        if self.page_counts < self.show_counts:
            # 判断总页数是不是小于要显示的页数
            range_start = 1
            range_end = self.page_counts
        else:
            # 总页数大于要显示的页数
            if self.current_page <= half_num + 1:
                range_start = 1
                range_end = self.show_counts
            elif half_num + 1 < self.current_page < page_counts - half_num:
                range_start = self.current_page - half_num
                range_end = self.current_page + half_num
            else:
                range_start = page_counts - self.show_counts + 1
                range_end = page_counts

        # 获取中间的页码标签
        middle = ""
        for num in range(range_start, range_end + 1):
            # 保留查询参数的路径
            self.params["page"] = num
            params = self.params.urlencode()  # condition=name&q=qwerqw&page=num

            # 判断哪一页是当前页，是的话，添加active效果

            if self.current_page == num:
                one_tag = f"""<li class="active"><a href="{self.request.path}?{params}">{num}</a></li>"""
            else:
                one_tag = f"""<li><a href="{self.request.path}?{params}">{num}</a></li>"""
            middle += one_tag

        # 设置下一页标签的url
        if self.current_page >= self.page_counts:
            # 如果当前页已经是最大页数，下一页禁用
            next = """
                <li disabled>
                    <a href="#" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>
                """
        else:
            # 如果不是正常使用
            self.params["page"] = self.current_page + 1
            params = self.params.urlencode()  # condition=name&q=qwerqw&page=num
            next = f"""
                <li>
                    <a href="{self.request.path}?{params}" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>
                """

        # 设置尾页标签url
        self.params["page"] = self.page_counts
        params = self.params.urlencode()  # condition=name&q=qwerqw&page=1
        if self.current_page == self.page_counts:
            last = f"""
                <li class="active">
                    <a href="{self.request.path}?{params}" aria-label="Previous">
                        <span aria-hidden="true">尾页</span>
                    </a>
                </li>
                """
        else:
            last = f"""
                <li>
                    <a href="{self.request.path}?{params}" aria-label="Previous">
                        <span aria-hidden="true">尾页</span>
                    </a>
                </li>
                """

        tag = f"""
            <nav aria-label="Page navigation">
                
                <ul class="pagination">
                    {first}
                    {previous}
                    {middle}
                    {next}
                    {last}
                    <li style="margin-right:10px"><span>共{self.page_counts}页</span></li>&nbsp
                </ul>
            </nav>
            """

        return tag

    def jump_page(self):
        """
        产生跳转页标签
        :return: 返回跳转页的标签
        """
        url = self.request.get_full_path()
        if not "/?" in url:
            url = url+"?page="
        else:
            if "page" in url:
                url = url.split("page")[0]+"page="
            else:
                url = url + "&page="


        jump_tag =f"""
        <div class="input-group input-group-sm">
            <span class="input-group-btn">跳转到</span>
            <input type="text" class="form-control" name="page" placeholder="跳转页码">
            <span class="input-group-btn">页</span>
            <span class="input-group-btn">
                <a id="jump_page" href="{url}" class="btn btn-info btn-flat">Go!</a>
            </span>
        </div>
        """
        return jump_tag

    def jump_js(self):
        """
        生成跳转页使用的js代码
        :return:
        """
        jump_js = """
            <script>
                $("#jump_page").click(function () {
                    var page = $("[name=page]").val();
                    var url = $(this).attr("href") + page;
                    $(this).attr("href", url);
                });
            </script>
            """
        return jump_js




