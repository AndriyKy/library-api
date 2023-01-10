from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from books.models import Book


class Borrowing(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="borrowing"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowing"
    )
    borrow_date = models.DateField(default=date.today)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    @staticmethod
    def validate_date(
        first_date: date,
        second_date: date,
        error_to_raise,
    ):
        """Raise error if the borrow date is less than the expected return date"""
        if first_date > second_date:
            raise error_to_raise(
                "The borrow date can`t be less than expected return date!"
            )

    def clean(self):
        Borrowing.validate_date(
            self.borrow_date,
            self.expected_return_date,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (
            f"{self.book} ({self.borrow_date} - {self.expected_return_date})"
        )

    class Meta:
        ordering = ["book", "borrow_date"]
