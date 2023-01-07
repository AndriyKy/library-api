from django.db import models


class Book(models.Model):
    class CoverOfBook(models.TextChoices):
        HARD = "H"
        SOFT = "F"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.CharField(max_length=1, choices=CoverOfBook.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=7, decimal_places=2)

    def get_cover(self):
        # Get label from choices enum
        cover_index = self.CoverOfBook.values.index(self.cover)
        return self.CoverOfBook.labels[cover_index]
