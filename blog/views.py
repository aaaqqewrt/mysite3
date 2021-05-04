import random
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from blog.forms import BlogForm, BlogTypeForm
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read


def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
    page_of_blogs = paginator.get_page(page_num)
    currentr_page_num = page_of_blogs.number  # 获取当前页码
    # 获取当前页码前后各2页的页码范围
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + \
                 list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context


def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    # context['rand_blogs'] = rand_blogs()
    return render(request, 'blog/blog_list.html', context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    # context['rand_blogs'] = rand_blogs(blog_type_pk )
    return render(request, 'blog/blogs_with_type.html', context)


def my_blog(request):
    blogs_all_list = Blog.objects.filter(author=request.user)
    context = get_blog_list_common_data(request, blogs_all_list)
    return render(request, 'blog/my_blog.html', context)


def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request, 'blog/blogs_with_date.html', context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    context = {}
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render(request, 'blog/blog_detail.html', context)  # 响应
    response.set_cookie(read_cookie_key, 'true')  # 阅读cookie标记
    return response


def new_blog_type(request):
    if request.method != 'POST':
        form = BlogTypeForm()
    else:
        form = BlogTypeForm(request.POST)
        if form.is_valid():
            new_blog_type = form.save(commit=False)
            new_blog_type.save()
            return HttpResponseRedirect(reverse('blog_list'))
    context = {'form': form}
    return render(request, 'blog/new_blog_type.html', context)


def new_blog(request, blog_type_id):
    blog_type = BlogType.objects.get(id=blog_type_id)
    if request.method != 'POST':
        form = BlogForm()
    else:
        form = BlogForm(data=request.POST)
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.blog_type = blog_type
            new_blog.save()
            return HttpResponseRedirect(reverse('blogs_with_type',
                                                args=[blog_type_id]))
    context = {'form': form, 'blog_type': blog_type}
    return render(request, 'blog/new_blog.html', context)


def edit_blog(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    blog_type = blog.blog_type
    if request.method != 'POST':
        form = BlogForm(instance=blog)
    else:
        form = BlogForm(instance=blog, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('blogs_with_type',
                                                args=[blog_type.id]))
    context = {'blog': blog, 'blog_type': blog_type, 'form': form}
    return render(request, 'blog/edit_blog.html', context)


@login_required
def safe_del_blog(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    blog.delete()
    return HttpResponseRedirect(reverse('blog_list'))

# def rand_blogs(except_id=0):
#     rand_count = 10
#     return Blog.objects.exclude(id=except_id).order_by('?')[:rand_count]
