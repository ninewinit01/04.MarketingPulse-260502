from django.db import models


class Industry(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name


class Keyword(models.Model):
    industry = models.ForeignKey(
        Industry, on_delete=models.CASCADE, related_name="keywords"
    )
    term = models.CharField(max_length=120)
    weight = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("industry__sort_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["industry", "term"], name="uniq_industry_term"
            )
        ]

    def __str__(self):
        return f"{self.industry.name}::{self.term}"
