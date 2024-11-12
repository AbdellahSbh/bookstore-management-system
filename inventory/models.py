from django.db import models

# Create your models here.

class Author(models.Model):

    name = models.CharField(max_length=255)

    bio = models.TextField(blank=True, null=True)



    def __str__(self):

        return self.name

    @classmethod
    def create(cls, name, bio):
        author = cls(name=name, bio=bio)
        author.save()
        return author



class Book(models.Model):

    title = models.CharField(max_length=255)

    authors = models.ManyToManyField(Author)  # Many-to-many relationship

    price = models.DecimalField(max_digits=6, decimal_places=2)

    stock_quantity = models.IntegerField(default=0)



    def __str__(self):

        return self.title

    @classmethod
    def create(cls, title, price, stock_quantity):
        book = cls(title=title, price=price, stock_quantity=stock_quantity)
        book.save()
        return book
