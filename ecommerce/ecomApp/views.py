from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Count
from .models import Product, Review, Category
from .serializer import *
import json
import os
import requests
from django.conf import settings
from django.core.files import File
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.http import HttpResponse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the data once to avoid reloading on every request
products = pd.read_json('C:\\Users\\hp\\Desktop\\smartfashionistawebsite\\back-end\\myenv\\ecommerce\\ecomApp\\products.json')
# Ensure the 'combined' feature exists and clustering is precomputed
if 'description' in products.columns and 'category' in products.columns:
    products['combined'] = products['category'] +' '+ products['description']
    vectorizer = TfidfVectorizer(
    stop_words='english',
    ngram_range=(1, 2),
    max_df=0.95,
    min_df=2
    )
    X = vectorizer.fit_transform(products['combined'])
    n_clusters = 10
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)
    products['cluster'] = kmeans.labels_

@api_view(['POST'])
def recommend_products(request):
    search_words = request.data.get('query', '')  # Get search words from request
    if not search_words:
        return Response({"error": "Query parameter is missing"}, status=400)
    
    # Transform the search words into a vector
    search_vector = vectorizer.transform([search_words])
    cluster_centroids = kmeans.cluster_centers_
    similarities = cosine_similarity(search_vector, cluster_centroids)
    most_similar_cluster = np.argmax(similarities)
    
    # Fetch top 3 products from the most similar cluster
    recommended_products = products[products['cluster'] == most_similar_cluster].head(3)
    recommended_list = recommended_products[['id','title', 'category','price','rating','description','image']].to_dict(orient='records')
    
    return Response({"recommended_products": recommended_list})
# Create your views here.
# get all products
@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products,many=True)
    return Response(serializer.data)
#get products by category
@api_view(['GET'])
def getProductsByCategory(request , category_name):
    id_category =Category.objects.filter(name=category_name)[0]
    products = Product.objects.filter(category=id_category)
    serializer = ProductSerializer(products,many=True)
    return Response(serializer.data)
#get product by id
@api_view(['GET'])
def get_product_detail(request ,product_id):
    product = Product.objects.filter(id=product_id)
    serializer = ProductSerializer(product,many=True)
    return Response(serializer.data)
@api_view(['GET'])
def get_most_popular_products(request):
    top_rated_products = Product.objects.order_by('-rating')[:8]
    # Serialize and return the products
    serializer = ProductSerializer(top_rated_products, many=True)
    return Response(serializer.data)
@api_view(['GET'])
def getCategories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories,many=True)
    return Response(serializer.data)


# Helper function to download an image from URL and save it
def download_image(url, product_slug, category_slug):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Get the image name and path
            image_name = os.path.basename(url)
            # Extraire le nom sans l'extension
            image_base, image_extension = os.path.splitext(image_name)
            # Prendre les 10 premières lettres du nom et ajouter l'extension
            short_image_name = image_base[:10] + image_extension

            # Construire le chemin complet
            image_path = os.path.join(settings.MEDIA_ROOT, category_slug, product_slug + short_image_name)

            # Create directories if they do not exist
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            # Save the image to the local file system
            with open(image_path, 'wb') as img_file:
                img_file.write(response.content)
            return image_path
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def import_data(request):
    # Load data from JSON
    try:
        default_user = User.objects.get(username='sihamadmin')
        file_path = 'C:\\Users\\hp\\Desktop\\django-rest-framework-react\\back-end\\myenv\\ecommerce\\ecomApp\\products.json'

        with open(file_path, 'r') as file:
            data = json.load(file)

        for item in data:
            # Create or get category
            category, created = Category.objects.get_or_create(name=item['category'])

            # Process reviews and create users
            for review in item.get('reviews', []):
                reviewer, created = User.objects.get_or_create(
                    email=review['reviewerEmail'],
                    defaults={
                        'username': review['reviewerName'],
                        'first_name': review['reviewerName'].split()[0],
                        'last_name': ' '.join(review['reviewerName'].split()[1:])
                    }
                )

            # Generate slugs for product and category
            product_slug = slugify(item['title'])
            category_slug = slugify(item['category'])

            # Get image URL from JSON data
            image_url = item['image']

            # Download image if URL exists
            image_file = None
            if image_url:
                image_file = download_image(image_url, product_slug, category_slug)
            # Create the product
            product = Product.objects.create(
                id=item['id'],
                title=item['title'],
                description=item['description'],
                category=category,
                price=item['price'],
                rating=item['rating'],
                stock=item['stock'],
                user=default_user,
                image=image_file,
            )
            image_name = os.path.basename(image_url)
            # Extraire le nom sans l'extension
            image_base, image_extension = os.path.splitext(image_name)
            # Prendre les 10 premières lettres du nom et ajouter l'extension
            short_image_name = image_base[:10] + image_extension
            # If image file exists, save the product image
            if image_file:
                product.image.name = f"{category_slug}/{product_slug}{short_image_name}"
                product.save()

            # Create reviews for the product
            for review in item.get('reviews', []):
                Review.objects.create(
                    product=product,
                    rating=review['rating'],
                    comment=review['comment'],
                    reviewer=reviewer
                )

        return HttpResponse("Data imported successfully!")

    except Exception as e:
        return HttpResponse(f"Error: {e}")