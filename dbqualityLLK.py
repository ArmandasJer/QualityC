import pymongo
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional, Dict

# Constants
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "advertisement_portal"
COLLECTION_USERS = "users"
COLLECTION_ADS = "advertisements"
COLLECTION_ARCHIVED_ADS = "archived_advertisements"
COLLECTION_COMMENTS = "comments"
ADDITIONAL_PROPERTIES_LABEL = "Additional Properties:"
MAX_ADS_LIMIT = 10

# Database Setup
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db[COLLECTION_USERS]
ads = db[COLLECTION_ADS]
archived_ads = db[COLLECTION_ARCHIVED_ADS]
comments = db[COLLECTION_COMMENTS]

# Helper Functions for Creating Records
def create_user(name: str, surname: str, registration_date: datetime, phone_number: str) -> ObjectId:
    user_data = {
        'name': name,
        'surname': surname,
        'registration_date': registration_date,
        'phone_number': phone_number
    }
    return users.insert_one(user_data).inserted_id

def create_advertisement(title: str, description: str, validity_days: int, category: str, user_id: ObjectId, additional_properties: Optional[Dict] = None) -> ObjectId:
    ad_data = {
        'title': title,
        'description': description,
        'validity_date': datetime.now() + timedelta(days=validity_days),
        'category': category,
        'user_id': user_id,
        'additional_properties': additional_properties or {},
    }
    return ads.insert_one(ad_data).inserted_id

def create_comment(advertisement_id: ObjectId, user_id: ObjectId, text: str) -> ObjectId:
    comment_data = {
        'advertisement_id': advertisement_id,
        'user_id': user_id,
        'text': text,
        'timestamp': datetime.now()
    }
    return comments.insert_one(comment_data).inserted_id

# Printing Helpers
def print_ad(ad: dict):
    print(f"Title: {ad['title']}")
    print(f"Description: {ad['description']}")
    print(f"Category: {ad['category']}")
    additional_properties = ad.get('additional_properties', {})
    if additional_properties:
        print(ADDITIONAL_PROPERTIES_LABEL)
        for key, value in additional_properties.items():
            print(f"  {key}: {value}")
    print("------")

def print_user_ads(user_id: ObjectId):
    user = users.find_one({'_id': user_id})
    if user:
        author_name = f"{user['name']} {user['surname']}"
        print(f"\nAdvertisements by {author_name}:")

        user_ads = ads.find({'user_id': user_id}).sort('validity_date', pymongo.DESCENDING).limit(MAX_ADS_LIMIT)
        for ad in user_ads:
            print_ad(ad)
    else:
        print(f"User with ID {user_id} not found.")

def print_newest_ads():
    print("Newest Advertisements:\n")
    newest_ads = ads.find().sort('validity_date', pymongo.DESCENDING).limit(MAX_ADS_LIMIT)
    for ad in newest_ads:
        print_ad(ad)

def print_ads_by_category(category: str):
    print(f"Advertisements in Category: {category}\n")
    category_ads = ads.find({'category': category}).sort('validity_date', pymongo.DESCENDING).limit(MAX_ADS_LIMIT)
    for ad in category_ads:
        user = users.find_one({'_id': ad['user_id']})
        author_name = f"{user['name']} {user['surname']}" if user else "Unknown"
        print(f"Author: {author_name}")
        print_ad(ad)

# Archiving Function
def archive_expired_ads():
    expired_ads = ads.find({'validity_date': {'$lt': datetime.now()}})
    for ad in expired_ads:
        archived_ads.insert_one(ad)
        ads.delete_one({'_id': ad['_id']})

# Advertisement Count by User
def print_user_ad_count(user_id: ObjectId):
    user_info = users.find_one({'_id': user_id})
    if user_info:
        user_name = f"{user_info['name']} {user_info['surname']}"
        ad_count = ads.count_documents({'user_id': user_id})
        print(f"Total advertisements by user {user_name}: {ad_count}")
    else:
        print(f"User with ID {user_id} not found.")

# Testing Function
def test_database():
    user_id = create_user('Armandas', 'Jereminas', datetime.now(), '123456789')
    user2_id = create_user('Nedas', 'Baranauskas', datetime.now(), '987654321')
    user3_id = create_user('Ramunas', 'Rudokas', datetime.now(), '123789456')

    ad1_id = create_advertisement('BMW M3 for sale', 'Pristine condition', 30, 'Automobile', user_id, {'manufacturer': 'BMW', 'mileage': 50000, 'VIN': 'ABC123'})
    ad2_id = create_advertisement('VW Golf for sale', 'Reliable, comfortable', 30, 'Automobile', user2_id, {'manufacturer': 'Volkswagen', 'mileage': 1000000, 'VIN': 'CBA321'})
    ad3_id = create_advertisement('Piano for sale', 'New, just shipped', 30, 'Musical Instruments', user2_id, {'brand': 'Fender', 'color': 'Dark Brown', 'condition': 'New'})

    print_newest_ads()
    print_user_ads(user2_id)
    print_ads_by_category('Automobile')
    print_user_ad_count(user2_id)
    archive_expired_ads()

    # Drop collections after testing
    db[COLLECTION_USERS].drop()
    db[COLLECTION_ADS].drop()
    db[COLLECTION_ARCHIVED_ADS].drop()
    db[COLLECTION_COMMENTS].drop()

# Run test
test_database()
