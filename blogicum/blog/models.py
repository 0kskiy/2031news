from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


User = get_user_model()


class PublishedCreated(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        verbose_name="Добавлено",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.is_published


class Post(PublishedCreated):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name="Заголовок",
    )
    text = models.TextField(
        blank=False,
        verbose_name="Text",
    )
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — можно делать "
            "отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name="posts",
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="posts",
        verbose_name="Категория",
    )
    image = models.ImageField(
        upload_to="posts_images",
        blank=True,
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self) -> str:
        return f'"{self.title}" от {self.pub_date}'

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.pk})


class Category(PublishedCreated):
    title = models.CharField(
        max_length=30,
        blank=False,
        verbose_name="Заголовок",
    )
    description = models.TextField(
        blank=False,
        verbose_name="Описание",
    )
    slug = models.SlugField(
        blank=False,
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; разрешены символы "
            "латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.title


class Location(PublishedCreated):
    name = models.CharField(
        max_length=30,
        blank=False,
        verbose_name="Название места",
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self) -> str:
        return self.name


class Comment(PublishedCreated):
    text = models.TextField(
        blank=False,
        verbose_name="Text",
    )
    author = models.ForeignKey(
        User,
        related_name="comments",
        verbose_name="Автор комментария",
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        verbose_name="Публикация",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.post.pk})
