from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView, \
    PostVersionComparisonView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('post/new', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/versions/', views.PostVersionListView.as_view(), name='post-versions'),
    path('post/<int:post_pk>/versions/<int:version_pk>/', PostVersionComparisonView.as_view(), name='version-comparison'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit-post'),
    path('post/<int:pk>/propose-edit/', views.propose_edit, name='propose-edit'),
    path('post/<int:pk>/proposals/', views.review_proposals, name='review-proposals'),
    path('post/<int:post_pk>/proposal/<int:proposal_pk>/', views.approve_proposal, name='approve-proposal'),
    path('search_engine/', views.search_engine, name='search_engine'),
    path('search_content/', views.search_content, name='search_content'),
    path('about/', views.about, name='blog-about'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)