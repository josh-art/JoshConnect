from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import UserPostListView, PostDetailView, PostCreateView, PostUpdateView, CommentUpdateView, PostDeleteview, \
    PostEditView, CommentDeleteView, GallaryDetailView
from rest_framework.routers import DefaultRouter
from .api import MessageModelViewSet, UserModelViewSet
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

router = DefaultRouter()
router.register(r'message', MessageModelViewSet, basename='message-api')
router.register(r'user', UserModelViewSet, basename='user-api')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
    path('ChatPage', login_required(
        TemplateView.as_view(template_name='core/chat.html')), name='chatting'),
    path('owino/', views.owino, name="owino"),
    path('owinoTech/', views.owino1, name="owino1"),
    path('login/', views.loginPage, name="login"),
    path('testimonial', views.testimonial, name='testimonial'),
    path('upload', views.upload, name='upload'),
    path('', views.index1, name='index'),
    path('like_post', views.like_post, name='like_post'),
    path('user/<str:username>', UserPostListView.as_view(), name='user_posts'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    #    path('post/<int:pk>', PostDetailsView.as_view(), name='post-detail'),
    path('post/<int:pk>/delete/', PostDeleteview.as_view(), name='post-delete'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post_update', views.post_update, name='post_update'),
    #    path('comment_update/<int:id>', views.comment_update, name='comment_update'),
    path('comment/<int:pk>/update', CommentUpdateView.as_view(), name='comment-update'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('favourite', views.favourite, name='favourite'),
    path('favourite_posts', views.favourite_posts, name='favourite_posts'),
    path('feedback/', views.contactForm, name='feedback'),
    path('Adverts/', views.AdvertForm, name='advertisement'),
    path('photo/', views.index, name='upload'),
    path('home/', views.home, name='home'),
    path('Advert/', views.advert, name='advert'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/', GallaryDetailView.as_view(), name='gallary_detail'),
    path('profile_posts', views.profile_posts, name='profile_posts'),
    path('profile_update', views.profile_update, name='profile_update'),
    path('handlesignup/', views.handlesignup, name="handlesignup"),
    path('handlelogin/', views.handlelogin, name="handlelogin"),
    path('signup/', views.signup, name="signup"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
