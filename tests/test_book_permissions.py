from django.contrib.auth import get_user_model
from django.contrib.auth.backends import UserModel
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book

BOOK_LIST_URL = reverse("books:book-list")


def _book_url_with_id(*args) -> str:
    return reverse(
        "books:book-detail",
        args=args,
    )


def _auth(email: str, staff: bool) -> (APIClient(), UserModel):
    client = APIClient()
    user = get_user_model().objects.create_user(
        email, "testpass", is_staff=staff
    )
    client.force_authenticate(user)

    return client, user


class BookPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_client, self.user = _auth("user@test.com", False)
        self.admin_client, self.admin_user = _auth("admin@test.com", True)

        self.think_like = {
            "title": "Think Like a Rocket Scientist",
            "author": "Ozan Varol",
            "cover": "S",
            "inventory": 5,
            "daily_fee": 1.73,
        }
        self.his_dark = {
            "title": "His Dark Materials",
            "author": "Philip Pullman",
            "cover": "H",
            "inventory": 1,
            "daily_fee": 0.55,
        }

    def test_book_creation_update_deletion(self):
        response_creation = self.admin_client.post(
            BOOK_LIST_URL, data=self.think_like
        )
        self.assertEqual(
            response_creation.status_code, status.HTTP_201_CREATED
        )

        response_update = self.admin_client.put(
            _book_url_with_id(response_creation.data["id"]),
            data=self.his_dark,
        )
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)

        response_deletion = self.admin_client.delete(
            _book_url_with_id(response_creation.data["id"]),
        )
        self.assertEqual(
            response_deletion.status_code, status.HTTP_204_NO_CONTENT
        )

    def test_anon_and_auth_access_for_read_only(self):
        response_creation = self.user_client.post(
            BOOK_LIST_URL, data=self.think_like
        )
        self.assertEqual(
            response_creation.status_code, status.HTTP_403_FORBIDDEN
        )

        self.admin_client.post(BOOK_LIST_URL, data=self.his_dark)
        self.admin_client.post(BOOK_LIST_URL, data=self.think_like)

        response_for_anon = self.client.get(BOOK_LIST_URL)
        self.assertEqual(response_for_anon.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_for_anon.data), 2)

        response_for_auth = self.user_client.get(BOOK_LIST_URL)
        self.assertEqual(response_for_auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_for_auth.data), 2)
