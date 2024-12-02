from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import Book
from .models import Author
import requests
from django.db import IntegrityError
from time import sleep


# Create a view to return the entire inventory as JSON
def sort_inventory(request):
    Title = request.GET.get('title', '')
    Price = request.GET.get('price','')
    if Price == 'Desc':
        Descprice = serializers.serialize('json', Book.objects.order_by('-price'))
        return JsonResponse(Descprice, safe=False)
    if Price == 'Asc':
        Ascprice = serializers.serialize('json', Book.objects.order_by('price'))
        return JsonResponse(Ascprice, safe=False)
    if Title == 'AtoZ':
        atoz = serializers.serialize('json', Book.objects.order_by('title'))
        return JsonResponse(atoz, safe=False)
    if Title == 'ZtoA':
        ztoa = serializers.serialize('json', Book.objects.order_by('-title'))
        return JsonResponse(ztoa, safe=False)
    if not Title:
        if not Price:
            books = serializers.serialize('json', Book.objects.all())
            return JsonResponse(books, safe=False)

def search_books(request):
    query_title = request.GET.get('title', '').strip()
    query_author = request.GET.get('author', '').strip()
    query_price = request.GET.get('price', '').strip()  

    if not query_title and not query_author:
        return JsonResponse({'error': 'At least one search parameter (title or author) is required.'}, status=400)


    api_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f"{'intitle:' + query_title if query_title else ''} {'inauthor:' + query_author if query_author else ''}",
        'maxResults': 10  
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        books = []
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            books.append({
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors', []),
                'publisher': volume_info.get('publisher'),
                'publishedDate': volume_info.get('publishedDate'),
                'description': volume_info.get('description'),
                'pageCount': volume_info.get('pageCount'),
                'categories': volume_info.get('categories'),
                'averageRating': volume_info.get('averageRating'),
                'ratingsCount': volume_info.get('ratingsCount'),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail'),
                'infoLink': volume_info.get('infoLink'),
            })

        return JsonResponse({'books': books}, status=200)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f"Failed to fetch books: {str(e)}"}, status=500)

def get_authors(request):
    authors = Author.objects.all()
    data = [
        {
            "id": author.id,
            "name": author.name,
            "bio": author.bio
        }
        for author in authors
    ]
    return JsonResponse(data, safe=False)

def add_authors(request):
    name = request.GET.get('name', '')
    bio = request.GET.get('bio', '')
    if not name:
        return JsonResponse({"error": "Author name is required."}, status=400)

    try:
        author, created = Author.objects.get_or_create(name=name, defaults={"bio": bio})
        return JsonResponse({
            "message": "Author created successfully!" if created else "Author already exists.",
            "author": {
                "id": author.id,
                "name": author.name,
                "bio": author.bio,
            }
        }, status=201 if created else 200)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

def add_books(request):
    Title = request.GET.get('title', '').strip()
    Authors = request.GET.get('authors', '').strip()
    Price = request.GET.get('price', '').strip()
    Stock_quantity = request.GET.get('stock', '').strip()

    if not Title:
        return JsonResponse({'error': 'Book title is required.'}, status=400)
    if not Authors:
        return JsonResponse({'error': 'At least one author is required.'}, status=400)
    if not Price:
        return JsonResponse({'error': 'Price is required.'}, status=400)
    if not Stock_quantity:
        return JsonResponse({'error': 'Stock quantity is required.'}, status=400)

    try:
        Price = float(Price)
        if Price <= 0:
            return JsonResponse({'error': 'Price must be a positive number.'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Price must be a valid number.'}, status=400)

    try:
        Stock_quantity = int(Stock_quantity)
        if Stock_quantity < 0:
            return JsonResponse({'error': 'Stock quantity must be a non-negative integer.'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Stock quantity must be a valid integer.'}, status=400)

    if Book.objects.filter(title=Title).exists():
        return JsonResponse({'error': 'A book with this title already exists.'}, status=400)

    author_names = [author_name.strip() for author_name in Authors.split(',')]
    author_objects = Author.objects.filter(name__in=author_names)
    if len(author_objects) != len(author_names):
        return JsonResponse({'error': 'Some authors were not found.'}, status=404)

    book = Book.objects.create(title=Title, price=Price, stock_quantity=Stock_quantity)
    book.authors.set(author_objects)

    return JsonResponse({
        'message': 'Book added successfully!',
        'book': {
            'title': book.title,
            'authors': [author.name for author in book.authors.all()],
            'price': book.price,
            'stock_quantity': book.stock_quantity,
        }
    }, status=201)

def delete_book(request):
    Title = request.GET.get('title', '').strip()

    if not Title:
        return JsonResponse({'error': 'Book title is required to delete the book.'}, status=400)

    try:
        book = get_object_or_404(Book, title=Title)
    except:
        return JsonResponse({'error': 'No book found with the provided title.'}, status=404)

    book.delete()
    return JsonResponse({'message': f"Book '{Title}' deleted successfully!"}, status=200)

def update_book(request):
    title = request.GET.get('title', '')
    new_title = request.GET.get('new_title', '')
    price = request.GET.get('price', '')
    stock_quantity = request.GET.get('stock', '')

    if not title:
        return JsonResponse({"error": "Current book title is required to identify the book."}, status=400)

    book = Book.objects.filter(title=title).first()
    if not book:
        return JsonResponse({"error": f"Book with title '{title}' does not exist."}, status=404)
    if new_title:
        book.title = new_title
    if price:
        try:
            book.price = float(price)
        except ValueError:
            return JsonResponse({"error": "Price must be a valid number."}, status=400)
    if stock_quantity:
        try:
            book.stock_quantity = int(stock_quantity)
        except ValueError:
            return JsonResponse({"error": "Stock quantity must be a valid integer."}, status=400)

    book.save()
    return JsonResponse({
        "message": f"Book '{title}' updated successfully!",
        "updated_fields": {
            "title": book.title,
            "price": book.price,
            "stock_quantity": book.stock_quantity
        }
    }, status=200)

def fetch_books_from_google(request):
    query = request.GET.get('q', '').strip()  
    if not query:
        return JsonResponse({"error": "A search query is required."}, status=400)


    api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40"
    books = []

    while api_url:

        try:
            response = requests.get(api_url)
            response.raise_for_status()  
            data = response.json()
            

            for item in data.get('items', []):
                book_info = item.get('volumeInfo', {})
                books.append({
                    "title": book_info.get('title', 'No Title'),
                    "authors": book_info.get('authors', ['Unknown Author']),
                    "published_date": book_info.get('publishedDate', 'Unknown Date'),
                    "description": book_info.get('description', 'No Description'),
                    "page_count": book_info.get('pageCount', 0),
                    "categories": book_info.get('categories', ['Uncategorized']),
                    "thumbnail": book_info.get('imageLinks', {}).get('thumbnail', None),
                })

            next_page_token = data.get('nextPageToken')
            if next_page_token:
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&pageToken={next_page_token}"
            else:
                api_url = None

            if not books:
                return JsonResponse({"error": "No books found from Google Books API."}, status=404)

            return JsonResponse(books, safe=False)

        except requests.RequestException as e:
            return JsonResponse({"error": f"Failed to fetch books from Google API: {str(e)}"}, status=500)

def fetch_and_add_book(request):
    title_query = request.GET.get('title', '').strip()

    if not title_query:
        return JsonResponse({'error': 'Book title is required.'}, status=400)


    url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{title_query}'
    response = requests.get(url)

    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch data from Google Books API.'}, status=500)

    data = response.json()


    if 'items' not in data or not data['items']:
        return JsonResponse({'error': f'No books found for the title "{title_query}".'}, status=404)

    book_data = data['items'][0]['volumeInfo']


    title = book_data.get('title', 'Unknown Title')
    authors = book_data.get('authors', [])
    price = 0.0 
    stock_quantity = 10  


    if Book.objects.filter(title=title).exists():
        return JsonResponse({'error': f"The book '{title}' already exists in the database."}, status=400)


    author_objects = []
    for author_name in authors:
        author, _ = Author.objects.get_or_create(name=author_name)
        author_objects.append(author)

    book = Book.objects.create(title=title, price=price, stock_quantity=stock_quantity)
    book.authors.set(author_objects)

    return JsonResponse({
        'message': 'Book added successfully from Google Books API!',
        'book': {
            'title': book.title,
            'authors': [author.name for author in book.authors.all()],
            'price': book.price,
            'stock_quantity': book.stock_quantity,
        }
    }, status=201)

def bulk_add_books(request):
    query = request.GET.get('q', '').strip()  
    if not query:
        return JsonResponse({"error": "A search query is required."}, status=400)

    max_books = 10000
    total_books_added = 0 
    books_to_create = []
    author_name_to_author = {}

    page = 1
    while total_books_added < max_books:
        start_index = (page - 1) * 40 
        api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&startIndex={start_index}"

        try:
            response = requests.get(api_url)
            response.raise_for_status() 
            data = response.json()

            if not data.get('items'):
                break

            for item in data.get('items', []):
                if total_books_added >= max_books:
                    break 

                book_info = item.get('volumeInfo', {})
                title = book_info.get('title', 'No Title')
                authors = book_info.get('authors', ['Unknown Author'])
                published_date = book_info.get('publishedDate', 'Unknown Date')
                description = book_info.get('description', 'No Description')
                page_count = book_info.get('pageCount', 0)
                categories = book_info.get('categories', ['Uncategorized'])
                thumbnail = book_info.get('imageLinks', {}).get('thumbnail', None)

                if Book.objects.filter(title=title).exists():
                    continue

                author_objects = []
                for author_name in authors:
                    author_name = author_name.strip()
                    if author_name not in author_name_to_author:
                        author, created = Author.objects.get_or_create(name=author_name)
                        author_name_to_author[author_name] = author
                    author_objects.append(author_name_to_author[author_name])


                book = Book(
                    title=title,
                    price = 0.0, 
                    stock_quantity = 10,
                )
                books_to_create.append(book)

                total_books_added += 1  

            if books_to_create:
                try:
                    if len(books_to_create) >= 1000:
                        Book.objects.bulk_create(books_to_create[:1000])
                        books_to_create = books_to_create[:1000]
                    else:
                        Book.objects.bulk_create(books_to_create)
                        books_to_create = []

                except IntegrityError as e:
                    return JsonResponse({'error': str(e)}, status=500)

            for book in books_to_create:
                book = Book.objects.get(id=book.id)
                for author in author_objects:
                    book.authors.add(author)

            books_to_create = []

            #sleep(0.25)

            if total_books_added >= max_books:
                break

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for page {page}: {e}")
            continue

    return JsonResponse({
        'message': f'{total_books_added} books added successfully!',
    }, status=201)


def bulk_delete_books(request):
    titles = request.GET.getlist('titles')
    if not titles:
        return JsonResponse({"error": "At least one title is required."}, status=400)

    titles = [title.strip() for title in titles]

    books_to_delete = Book.objects.filter(title__in=titles)

    if not books_to_delete.exists():
        return JsonResponse({"error": "No books found with the provided titles."}, status=404)

    batch_size = 500  
    deleted_count = 0

    while True:
        books_batch_ids = books_to_delete.values_list('id', flat=True)[:batch_size]
        
        if not books_batch_ids:
            break
        
        deleted_batch_count, _ = Book.objects.filter(id__in=books_batch_ids).delete()

        deleted_count += deleted_batch_count

        if deleted_batch_count == 0:
            break

    return JsonResponse({
        "message": f"{deleted_count} book(s) deleted successfully."
    }, status=200)
