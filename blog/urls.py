from django.conf.urls import url
from django.urls import path
from . import views

# start with blog
# app_name = 'blog'
urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('new_blog_type/', views.new_blog_type, name='new_blog_type'),
    url(r'^new_blog/(?P<blog_type_id>\d+)/$', views.new_blog, name='new_blog'),
    path('<int:blog_pk>', views.blog_detail, name="blog_detail"),
    url(r'^edit_blog/(?P<blog_id>\d+)/$', views.edit_blog, name='edit_blog'),
    url(r'^safe_del_blog/(?P<blog_id>\d+)/$', views.safe_del_blog, name='safe_del_blog'),
    path('type/<int:blog_type_pk>', views.blogs_with_type, name="blogs_with_type"),
    path('my_blog/', views.my_blog, name="my_blog"),
    path('date/<int:year>/<int:month>', views.blogs_with_date, name="blogs_with_date"),
]


# http://localhost:8000/blog/
# path('<int:blog_id>', views.safe_del_blog, name="safe_del_blog"),
# re_path('safe_del_blog/(?P<blog_id>d+)/',views.safe_del_blog,name='safe_del_blog'),
# path('new_blog/(?<blog_type _id>\d+)/', views.new_blog, name='new_blog'),
