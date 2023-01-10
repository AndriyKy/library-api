from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers

from books.serializer import BookListSerializer
from borrowings.models import Borrowing
from books.models import Book


class BorrowingSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateField(
        help_text="The default is today's date"
    )

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)

        book_instance = Book.objects.get(id=attrs["book"].id)
        if book_instance.inventory < 1:
            raise serializers.ValidationError(
                "A copy of the book is not available yet!"
            )

        Borrowing.validate_date(
            data["borrow_date"],
            data["expected_return_date"],
            serializers.ValidationError,
        )

        return data

    def create(self, validated_data):
        with transaction.atomic():
            book_instance = Book.objects.get(id=validated_data["book"].id)
            book_instance.inventory -= 1
            book_instance.save()
            return Borrowing.objects.create(**validated_data)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
        )


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingDetailSerializer(BorrowingListSerializer):
    book = BookListSerializer(many=False, read_only=True)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingReturnSerializer, self).validate(attrs=attrs)
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError(
                "The book has already been returned"
            )
        return data

    def update(self, instance, validated_data):
        with transaction.atomic():
            book_instance = Book.objects.get(id=instance.book.id)
            book_instance.inventory += 1
            book_instance.save()

            instance.actual_return_date = now().date().today()
            instance.save()
            return instance

    class Meta(BorrowingListSerializer.Meta):
        read_only_fields = BorrowingListSerializer.Meta.fields
