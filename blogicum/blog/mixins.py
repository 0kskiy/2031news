from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Model
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse


class MyLoginRequiredMixin(LoginRequiredMixin):
    login_url = "/auth/login/"
    model = None


class PostLoginRequiredMixin(MyLoginRequiredMixin):
    action = None

    def dispatch(self, request, *args, **kwargs):
        if self.action != "create":
            self.object = get_object_or_404(self.model, pk=kwargs["pk"])
            if request.user != self.object.author:
                if self.action == "edit":
                    return redirect(self.object.get_absolute_url())
                else:
                    raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.action == "delete":
            return reverse("blog:index")
        elif self.action == "create":
            return reverse(
                "blog:profile",
                kwargs={
                    "slug": self.object.author.username,
                },
            )
        else:
            return self.object.get_absolute_url()


class CommentLoginRequiredMixin(MyLoginRequiredMixin):
    action = None

    def dispatch(self, request, *args, **kwargs):
        if self.action != "create":
            if request.user.is_anonymous:
                raise Http404
            get_object_or_404(self.model, pk=kwargs["pk"], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class PaginatorHelperMixin:
    paginate_by = 1

    def paginate_list(
        self, objects_list: list[Model], paginate_by=paginate_by
    ):
        paginator = Paginator(objects_list, paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj
