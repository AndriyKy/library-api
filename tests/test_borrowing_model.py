from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )

        self.his_dark = Book.objects.create(
            title="His Dark Materials",
            author="Philip Pullman",
            cover="Hard",
            inventory=10,
            daily_fee=0.55,
        )

    def test_validation_date(self):
        borrow_date = datetime(year=2023, month=1, day=9).date()
        expected_return_date = datetime(year=2023, month=1, day=8).date()

        try:
            Borrowing.objects.create(
                user=self.user,
                book=self.his_dark,
                borrow_date=borrow_date,
                expected_return_date=expected_return_date,
            )
        except ValidationError as ve:
            self.assertEqual(
                ve.messages,
                ["The borrow date can`t be less than expected return date!"],
            )
