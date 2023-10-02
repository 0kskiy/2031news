from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    ListView,
)
from django.db.models import Count

from .forms import PostForm, CommentForm
from .mixins import (
    CommentLoginRequiredMixin,
    MyLoginRequiredMixin,
    PostLoginRequiredMixin,
    PaginatorHelperMixin,
)
from .models import Post, Category, User, Comment
from .constans import DETAIL_VIEW_PAGINATE_BY


class PostCreateView(PostLoginRequiredMixin, CreateView):
    model = Post
    template_name = "blog/create.html"
    form_class = PostForm
    action = "create"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(PostLoginRequiredMixin, UpdateView):
    model = Post
    template_name = "blog/create.html"
    form_class = PostForm
    action = "edit"


class PostDeleteView(PostLoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    form_class = PostForm
    action = "delete"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    queryset = Post.objects.select_related("location", "category")

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs["pk"])
        if self.request.user != self.object.author:
            get_object_or_404(
                Post,
                pk=kwargs["pk"],
                is_published=True,
                category__is_published=True,
                pub_date__lt=timezone.now(),
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.filter(
            is_published=True,
        ).select_related("author")
        return context


class PostListView(ListView):
    model = Post
    template_name = "blog/index.html"
    ordering = "-pub_date"
    paginate_by = 10
    queryset = (
        Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        .select_related("location", "category")
        .annotate(comment_count=Count("comments"))
    )


class CommentCreateView(CommentLoginRequiredMixin, CreateView):
    post_id = None
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    action = "create"

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_id
        return super().form_valid(form)


class CommentUpdateView(CommentLoginRequiredMixin, UpdateView):
    model = Comment
    fields = ("text",)
    template_name = "blog/comment.html"


class CommentDeleteView(CommentLoginRequiredMixin, DeleteView):
    model = Comment
    fields = ("text",)
    template_name = "blog/comment.html"


class UserDetailView(DetailView, PaginatorHelperMixin):
    model = User
    slug_field = "username"
    context_object_name = "profile"
    template_name = "blog/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.object.posts.select_related(
            "location", "category"
        ).order_by("-pub_date").annotate(comment_count=Count("comments"))
        if self.request.user != self.object:
            posts = posts.filter(
                is_published=True,
                category__is_published=True,
            )
        page_obj = self.paginate_list(posts, DETAIL_VIEW_PAGINATE_BY)
        context["page_obj"] = page_obj
        return context


class EditProfileView(MyLoginRequiredMixin, UpdateView):
    model = User
    fields = (
        "first_name",
        "last_name",
        "email",
    )
    template_name = "blog/user.html"

    def get_object(self, *args, **kwargs):
        return self.request.user

    def get_success_url(self) -> str:
        return reverse("blog:profile", kwargs={"slug": self.object.username})


class CategoryDetailView(DetailView, PaginatorHelperMixin):
    model = Category
    slug_field = "slug"
    template_name = "blog/category.html"
    queryset = Category.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = (
            self.object.posts.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
            .select_related("location", "category")
            .order_by("-pub_date")
        )
        context["page_obj"] = self.paginate_list(
            posts, DETAIL_VIEW_PAGINATE_BY
        )
        return context
