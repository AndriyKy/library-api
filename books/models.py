from django.db import models


class Book(models.Model):
    class CoverOfBook(models.TextChoices):
        HARD = "H"
        SOFT = "S"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.CharField(max_length=1, choices=CoverOfBook.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=7, decimal_places=2)

    @property
    def get_cover(self) -> str:
        # Get label from choices enum
        cover_index = self.CoverOfBook.values.index(self.cover)
        return self.CoverOfBook.labels[cover_index]

    def __str__(self):
        return f"{self.title} ({self.author})"
