from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from users.forms import FileForm, PostForm
from django.db.models import Q


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        if Post.visibility:
            user = get_object_or_404(User, username=self.kwargs.get('username'))
            return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


def search_engine(request):
    if request.method == "POST":
        searched = request.POST.get('searched')
        posts_title = Post.objects.filter(title__icontains=searched)
        posts_content = Post.objects.filter(content__icontains=searched)
        return render(request, 'blog/search_engine.html', {'searched': searched, 'posts_title': posts_title, 'posts_content': posts_content})
    else:
        return render(request, 'blog/search_engine.html', {})


def search_content(request):
    if request.method == "POST":
        searched_content = request.POST.get('searched_content')
        posts_content = Post.objects.filter(content__icontains=searched_content)
        return render(request, 'blog/search_content.html', {'searched_content': searched_content, 'posts_content': posts_content})
    else:
        return render(request, 'blog/search_content.html', {})
