from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import UserModel
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing

BORROWING_LIST_URL = reverse("borrowings:borrowing-list")


def _borrowing_return_url(*args) -> str:
    return reverse(
        "borrowings:borrowing-return-book",
        args=args,
    )


def _auth(email: str, staff: bool) -> (APIClient(), UserModel):
    client = APIClient()
    user = get_user_model().objects.create_user(
        email, "testpass", is_staff=staff
    )
    client.force_authenticate(user)

    return client, user


class BorrowingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_client, self.user = _auth("user@test.com", False)
        self.admin_client, self.admin_user = _auth("admin@test.com", True)

        self.borrow_date = datetime(year=2023, month=1, day=9).date()
        self.expected_return_date = datetime(year=2023, month=1, day=15).date()

        think_like = Book.objects.create(
            title="Think Like a Rocket Scientist",
            author="Ozan Varol",
            cover="Soft",
            inventory=5,
            daily_fee=1.73,
        )
        user_borrowing = {
            "user": self.user.pk,
            "book": think_like.pk,
            "borrow_date": self.borrow_date,
            "expected_return_date": self.expected_return_date,
        }
        self.admin_client.post(BORROWING_LIST_URL, data=user_borrowing)

        self.his_dark = Book.objects.create(
            title="His Dark Materials",
            author="Philip Pullman",
            cover="Hard",
            inventory=1,
            daily_fee=0.55,
        )
        self.admin_borrowing = {
            "user": self.admin_user.pk,
            "book": self.his_dark.pk,
            "borrow_date": self.borrow_date,
            "expected_return_date": self.expected_return_date,
        }
        self.post_response = self.admin_client.post(
            BORROWING_LIST_URL, data=self.admin_borrowing
        )

    def test_borrowing_permissions(self):
        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user_response = self.user_client.get(BORROWING_LIST_URL)
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(user_response.data), 1)

        admin_response = self.admin_client.get(BORROWING_LIST_URL)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(admin_response.data), 2)

    def test_borrowing_creation(self):
        self.assertEqual(
            self.post_response.status_code, status.HTTP_201_CREATED
        )

        book = Book.objects.get(id=self.post_response.data["book"])
        self.assertEqual(
            book.inventory,
            self.his_dark.inventory - 1,
            "When borrowing, the number of books must be reduced by 1",
        )

        borrowing_obj = Borrowing.objects.get(id=self.post_response.data["id"])
        self.assertEqual(self.admin_user.id, borrowing_obj.user_id)
        self.assertEqual(self.his_dark.pk, borrowing_obj.book_id)

        error_response = self.admin_client.post(
            BORROWING_LIST_URL, data=self.admin_borrowing
        )
        self.assertEqual(
            error_response.status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            error_response.data["non_field_errors"],
            ["A copy of the book is not available yet!"],
        )

    def test_borrowing_return(self):
        patch_response = self.admin_client.patch(
            _borrowing_return_url(self.post_response.data["id"])
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        book = Book.objects.get(id=self.post_response.data["book"])
        self.assertEqual(
            book.inventory,
            self.his_dark.inventory,
            "When returning the borrowing, the number of books must be increased by 1",
        )

        error_response = self.admin_client.patch(
            _borrowing_return_url(self.post_response.data["id"])
        )
        self.assertEqual(
            error_response.status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            error_response.data["non_field_errors"],
            ["The book has already been returned"],
        )

    def test_borrowing_filtering(self):
        active_borrowing_response = self.admin_client.get(
            BORROWING_LIST_URL, {"is_active": True}
        )
        self.assertEqual(len(active_borrowing_response.data), 2)

        user_borrowings_response = self.admin_client.get(
            BORROWING_LIST_URL, {"user_id": self.user.id}
        )
        self.assertEqual(len(user_borrowings_response.data), 1)
        self.assertEqual(
            user_borrowings_response.data[0]["user"], self.user.id
        )

        inactive_borrowing_response = self.user_client.get(
            BORROWING_LIST_URL, {"is_active": False}
        )
        self.assertEqual(len(inactive_borrowing_response.data), 0)

        user_borrowings_response = self.user_client.get(
            BORROWING_LIST_URL, {"user_id": self.admin_user.id}
        )
        self.assertNotEqual(
            user_borrowings_response.data[0]["user"], self.admin_user.id
        )
