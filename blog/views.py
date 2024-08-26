from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, PostVersion
from users.forms import FileForm, PostForm
from difflib import HtmlDiff
from django.db.models import Q
from django.views import View
from difflib import Differ

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import PostEditProposal
from users.forms import PostForm, PostEditProposalForm
from django.utils import timezone
from django.core.exceptions import PermissionDenied


def user_in_collaboration_group(user, post):
    if post.co_creation_group:
        # Check if the user is the owner of the group
        if user == post.co_creation_group.owner:
            return True

        # Check if the user is a member of the group
        return user in post.co_creation_group.members.all()
    return False



def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Check if co-creation is enabled and the mode is open
    if not post.co_creation_enabled or post.co_creation_mode != 'open':
        messages.error(request, "Edytowanie tego posta nie jest dozwolone.")
        return redirect('post-detail', pk=post.pk)

    # Check if the user is part of the collaboration group, the owner of the group, or the author
    if not user_in_collaboration_group(request.user, post) and request.user != post.author:
        messages.error(request, "Nie masz uprawnień do edycji tego posta.")
        return redirect('post-detail', pk=post.pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post został pomyślnie zaktualizowany.")
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/post_edit.html', context)


@login_required
def propose_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Check if co-creation is enabled and the mode is closed
    if not post.co_creation_enabled or post.co_creation_mode != 'closed':
        messages.error(request, "Proponowanie zmian dla tego posta nie jest dozwolone.")
        return redirect('post-detail', pk=post.pk)

    # Check if the user is part of the collaboration group or the author
    if not user_in_collaboration_group(request.user, post) and request.user != post.author:
        messages.error(request, "Nie masz uprawnień do proponowania zmian dla tego posta.")
        return redirect('post-detail', pk=post.pk)

    # Process the proposal form
    if request.method == 'POST':
        form = PostEditProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.post = post
            proposal.proposer = request.user
            proposal.save()
            messages.success(request, "Twoja propozycja zmian została przesłana do zatwierdzenia.")
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostEditProposalForm(initial={'title': post.title, 'content': post.content})

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/propose_edit.html', context)


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


@login_required
def review_proposals(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        messages.error(request, "Nie masz uprawnień do przeglądania propozycji zmian dla tego posta.")
        return redirect('post-detail', pk=post.pk)

    proposals = post.edit_proposals.filter(is_approved=None)

    context = {
        'post': post,
        'proposals': proposals
    }
    return render(request, 'blog/review_proposals.html', context)


@login_required
def approve_proposal(request, post_pk, proposal_pk):
    post = get_object_or_404(Post, pk=post_pk)
    proposal = get_object_or_404(PostEditProposal, pk=proposal_pk, post=post)

    if request.user != post.author:
        messages.error(request, "Nie masz uprawnień do zatwierdzania tej propozycji.")
        return redirect('post-detail', pk=post.pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            post.title = proposal.title
            post.content = proposal.content
            post.save()
            proposal.is_approved = True
            proposal.date_reviewed = timezone.now()
            proposal.save()
            messages.success(request, "Propozycja została zatwierdzona i zmiany zostały zastosowane.")
        elif action == 'reject':
            proposal.is_approved = False
            proposal.date_reviewed = timezone.now()
            proposal.save()
            messages.success(request, "Propozycja została odrzucona.")
        return redirect('review-proposals', pk=post.pk)

    context = {
        'post': post,
        'proposal': proposal
    }
    return render(request, 'blog/approve_proposal.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user

        return Post.objects.filter(
            Q(visibility=True) |  # Posts visible to everyone
            Q(group__members=user) |  # Posts visible to the group members
            Q(group__owner=user)  # Posts visible to the group owner
        ).distinct().order_by('-date_posted')


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        profile_user = get_object_or_404(User, username=self.kwargs.get('username'))

        # Get posts authored by the profile user, visible to everyone, or specifically to this user's groups
        return Post.objects.filter(
            Q(author=profile_user) &
            (Q(visibility=True) |
            Q(group__members=user) |
            Q(group__owner=user))
        ).distinct().order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        user = self.request.user

        if post.visibility or user == post.author or user == post.group.owner or user in post.group.members.all():
            return post
        else:
            raise PermissionDenied("You do not have permission to view this post.")


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
        post = form.save(commit=False)

        # Get the latest version number
        latest_version = post.versions.first()
        version_number = latest_version.version_number + 1 if latest_version else 1

        # Save the new version
        PostVersion.objects.create(
            post=post,
            version_number=version_number,
            title=post.title,
            content=post.content,
            uploaded_file=post.uploaded_file,
            author=self.request.user
        )

        post.save()
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user in post.co_creation_group.members.all()


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def highlight_changes(old_content, new_content):
    differ = Differ()
    diff = list(differ.compare(old_content.splitlines(), new_content.splitlines()))

    html_diff = []
    for line in diff:
        if line.startswith('+ '):
            html_diff.append(f"<ins style='background:#e6ffe6;'>{line[2:]}</ins><br>")
        elif line.startswith('- '):
            html_diff.append(f"<del style='background:#ffe6e6;'>{line[2:]}</del><br>")
        elif line.startswith('? '):
            continue  # Ignore lines with markers
        else:
            html_diff.append(f"{line[2:]}<br>")

    return ''.join(html_diff)


class PostVersionComparisonView(LoginRequiredMixin, View):
    template_name = 'blog/version_comparison.html'

    def get(self, request, post_pk, version_pk):
        post = get_object_or_404(Post, pk=post_pk)
        version = get_object_or_404(PostVersion, pk=version_pk)

        # Find the previous version
        previous_version = PostVersion.objects.filter(post=post, version_number__lt=version.version_number).order_by('-version_number').first()

        if previous_version:
            highlighted_changes = highlight_changes(previous_version.content, version.content)
        else:
            highlighted_changes = "<p>Brak wcześniejszej wersji do porównania.</p>"

        context = {
            'post': post,
            'version': version,
            'previous_version': previous_version,
            'highlighted_changes': highlighted_changes
        }
        return render(request, self.template_name, context)


class PostVersionListView(LoginRequiredMixin, ListView):
    model = PostVersion
    template_name = 'blog/post_versions.html'
    context_object_name = 'versions'

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        versions = post.versions.all()

        if versions.exists():
            # Add highlighted differences to each version
            for i in range(len(versions)):
                if i < len(versions) - 1:
                    versions[i].highlighted_changes = highlight_changes(versions[i + 1].content, versions[i].content)
                else:
                    versions[i].highlighted_changes = None  # No comparison for the first version
        return versions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


def search_engine(request):
    if request.method == "POST":
        searched = request.POST.get('searched')
        posts_title = Post.objects.filter(title__icontains=searched)
        posts_content = Post.objects.filter(content__icontains=searched)
        authors = User.objects.filter(username__icontains=searched)
        return render(request, 'blog/search_engine.html',
                      {'searched': searched, 'posts_title': posts_title, 'posts_content': posts_content,
                       'authors': authors})
    else:
        return render(request, 'blog/search_engine.html', {})


def search_content(request):
    if request.method == "POST":
        searched_content = request.POST.get('searched_content')
        posts_content = Post.objects.filter(content__icontains=searched_content)
        return render(request, 'blog/search_content.html', {'searched_content': searched_content, 'posts_content': posts_content})
    else:
        return render(request, 'blog/search_content.html', {})
