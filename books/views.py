from rest_framework import viewsets

from books.models import Book
from books.serializer import (
    BookSerializer,
    BookListSerializer,
)
from books.permissions import IsAdminOrIfAnonReadOnly


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAnonReadOnly,)

    def get_serializer_class(self):
        if self.action in (
            "list",
            "retrieve",
        ):
            return BookListSerializer
        return BookSerializer
