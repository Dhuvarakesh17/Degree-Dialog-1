import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import os
import pymongo
import jwt
from datetime import datetime, timedelta
import cohere

# Load API key
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
cohere_client = cohere.Client(COHERE_API_KEY)

# MongoDB setup - MUST have MONGO_URI set, no localhost fallback
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "degreedialog")

# Validate configuration
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is required! Set it on your deployment platform.")

# Debug: Log environment variable status
print(f"MONGO_URI set: {bool(MONGO_URI)}")
print(f"MONGO_URI starts with: {MONGO_URI[:30]}..." if MONGO_URI else "MONGO_URI is None")
print(f"MONGO_DB_NAME: {MONGO_DB_NAME}")
print(f"COHERE_API_KEY set: {bool(os.getenv('COHERE_API_KEY'))}")

# MongoDB connection
mongo_client = None
try:
    print(f"Attempting MongoDB connection to: {MONGO_URI[:30]}...")
    mongo_client = pymongo.MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=15000,
    )
    # Test connection
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"✗ MongoDB connection error: {e}")
    print("WARNING: MongoDB is not available. Check your credentials in MONGO_URI")
    mongo_client = None

mongo_db = None
users_collection = None
chats_collection = None

if mongo_client:
    mongo_db = mongo_client[MONGO_DB_NAME]
    users_collection = mongo_db["users"]
    chats_collection = mongo_db["chats"]
else:
    print("WARNING: Database collections not initialized")


# Root API endpoint
@api_view(['GET', 'HEAD'])
@permission_classes([AllowAny])
def root_view(request):
    """Root API endpoint - provides API status"""
    return Response({
        "message": "Degree Dialog API",
        "status": "running",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register/",
                "login": "POST /api/auth/login/",
                "profile": "GET /api/auth/profile/",
            },
            "chat": {
                "message": "POST /api/chat/",
                "history": "GET /api/chat/history/",
                "clear": "DELETE /api/chat/clear/",
            }
        },
        "mongodb": "connected" if mongo_client else "disconnected - check MONGO_URI credentials",
        "cohere": "configured" if COHERE_API_KEY else "not configured"
    }, status=status.HTTP_200_OK)


def _handle_mongo_error(error_msg="Database connection failed"):
    """Helper to handle MongoDB connection errors"""
    print(f"MongoDB Error: {error_msg}")
    import traceback
    traceback.print_exc()
    
    # Check if it's an authentication error
    if "bad auth" in str(error_msg).lower() or "authentication failed" in str(error_msg).lower():
        return Response(
            {
                "error": "Database authentication failed",
                "details": "Check your MongoDB Atlas credentials. Ensure MONGO_URI environment variable is set correctly with valid username and password."
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            "error": "Database service temporarily unavailable. Please check your MongoDB Atlas connection.",
            "details": str(error_msg)
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE
    )


def _generate_tokens(user_id):
    access_payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
    }
    refresh_payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    access = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")
    refresh = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")
    return access, refresh


def _get_user_from_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None
        try:
            return users_collection.find_one({"_id": user_id})
        except pymongo.errors.OperationFailure as e:
            print(f"MongoDB authentication error: {e}")
            raise Exception("Database authentication failed") from e
        except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.NetworkTimeout) as e:
            print(f"MongoDB connection timeout: {e}")
            raise Exception("Database connection failed") from e
        except Exception as e:
            print(f"MongoDB query error: {e}")
            raise
    except jwt.PyJWTError:
        return None


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """User registration endpoint"""
    try:
        if not users_collection:
            return Response(
                {'error': 'Database service unavailable. Check MongoDB Atlas connection.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        print(
            "Register attempt",
            {
                "username": username,
                "email": email,
                "password_len": len(password) if password else 0,
            },
        )

        if not username or not email or not password:
            return Response(
                {'error': 'Please provide username, email, and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            username_exists = users_collection.find_one({"username": username}) is not None
            email_exists = users_collection.find_one({"email": email}) is not None
        except pymongo.errors.OperationFailure as e:
            print(f"MongoDB authentication error during registration: {e}")
            return Response(
                {'error': 'Database authentication failed. Please contact support.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.NetworkTimeout) as e:
            print(f"MongoDB connection timeout during registration: {e}")
            return Response(
                {'error': 'Database connection timeout. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        print(
            "Register validation",
            {"username_exists": username_exists, "email_exists": email_exists},
        )

        if username_exists:
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_409_CONFLICT
            )

        if email_exists:
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_409_CONFLICT
            )
        
        user_doc = {
            "_id": username,
            "username": username,
            "email": email,
            "password": make_password(password),
            "created_at": datetime.utcnow(),
        }
        
        try:
            users_collection.insert_one(user_doc)
        except pymongo.errors.OperationFailure as e:
            print(f"MongoDB authentication error during insert: {e}")
            return Response(
                {'error': 'Database authentication failed. Please contact support.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.NetworkTimeout) as e:
            print(f"MongoDB connection timeout during insert: {e}")
            return Response(
                {'error': 'Database connection timeout. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        access_token, refresh_token = _generate_tokens(user_doc["_id"])
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user_doc["_id"],
                'username': user_doc["username"],
                'email': user_doc["email"],
            },
            'tokens': {
                'refresh': refresh_token,
                'access': access_token,
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        import traceback
        print(f"Registration error: {repr(e)}")
        traceback.print_exc()
        return Response(
            {'error': 'An unexpected error occurred during registration'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    try:
        if not users_collection:
            return Response(
                {'error': 'Database service unavailable. Check MongoDB Atlas connection.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        print(f"Login attempt - Username: {username}, Password: {'*' * len(password) if password else None}")
        
        if not username or not password:
            return Response(
                {'error': 'Please provide username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_doc = users_collection.find_one({"username": username})
            print(f"Authentication result: {user_doc is not None}")
        except pymongo.errors.OperationFailure as e:
            print(f"MongoDB authentication error: {e}")
            return Response(
                {'error': 'Database authentication failed. Please contact support. Check your MongoDB Atlas credentials.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.NetworkTimeout) as e:
            print(f"MongoDB connection timeout: {e}")
            return Response(
                {'error': 'Database connection timeout. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if not user_doc or not check_password(password, user_doc.get("password", "")):
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        access_token, refresh_token = _generate_tokens(user_doc["_id"])
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user_doc["_id"],
                'username': user_doc["username"],
                'email': user_doc["email"],
            },
            'tokens': {
                'refresh': refresh_token,
                'access': access_token,
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        import traceback
        print(f"Login error: {repr(e)}")
        traceback.print_exc()
        return Response(
            {'error': 'An unexpected error occurred during login'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def user_profile_view(request):
    """Get current user profile"""
    user_doc = _get_user_from_token(request)
    if not user_doc:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({
        'id': user_doc["_id"],
        'username': user_doc["username"],
        'email': user_doc["email"],
    })


# System instruction to make Gemini act as a college advisor
COLLEGE_ADVISOR_PROMPT = """
You are an AI College Advisor assistant. Your role is to provide helpful, accurate information 
about all aspects of college education. This includes but is not limited to:

- Admissions processes and requirements
- Courses and academic programs
- Scholarships and financial aid
- Campus facilities and student life
- Career opportunities after graduation
- College rankings and comparisons
- Study tips and academic advice
- Extracurricular activities
- Any other higher education related queries

For questions outside this scope, politely inform the user that you specialize in college-related 
topics. Be friendly, professional, and provide detailed, accurate information. If you don't know 
an answer, say so rather than making up information.
"""

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_view(request):
    """Chatbot endpoint - requires authentication"""
    try:
        user_doc = _get_user_from_token(request)
        if not user_doc:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return _handle_mongo_error(str(e))
    
    if request.method == "POST":
        user_message = request.data.get("message", "").strip()

        if not user_message:
            return Response(
                {"response": "Please type your question about college or higher education."}
            )

        try:
            # Use Cohere Chat API (Generate API deprecated as of Sept 15, 2025)
            # Prepend system prompt to user message since chat() doesn't have system param
            full_message = f"{COLLEGE_ADVISOR_PROMPT}\n\nUser question: {user_message}"
            
            response = cohere_client.chat(
                message=full_message,
            )

            bot_reply = response.text.strip() if response.text else "I'm not sure how to answer that."

            # Store messages in MongoDB
            try:
                username = user_doc["_id"]
                chat_entry = {
                    "username": username,
                    "messages": [
                        {
                            "role": "user",
                            "content": user_message,
                            "timestamp": datetime.utcnow()
                        },
                        {
                            "role": "bot",
                            "content": bot_reply,
                            "timestamp": datetime.utcnow()
                        }
                    ],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                chats_collection.insert_one(chat_entry)
            except pymongo.errors.OperationFailure as db_err:
                print(f"Warning: Chat not saved to database (auth error): {db_err}")
                # Still return the response even if storage fails
            except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.NetworkTimeout) as db_err:
                print(f"Warning: Chat not saved to database (connection error): {db_err}")
                # Still return the response even if storage fails

            return Response({"response": bot_reply})

        except Exception as e:
            print(f"Chatbot error: {repr(e)}")
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_history_view(request):
    """Get user's chat history"""
    try:
        user_doc = _get_user_from_token(request)
        if not user_doc:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return _handle_mongo_error(str(e))

    try:
        username = user_doc["_id"]
        
        # Fetch all chat entries for this user, sorted by newest first
        chat_entries = list(chats_collection.find(
            {"username": username},
            sort=[("created_at", -1)]
        ))

        # Convert ObjectId to string for JSON serialization
        for entry in chat_entries:
            entry["_id"] = str(entry["_id"])

        return Response({
            "chats": chat_entries
        }, status=status.HTTP_200_OK)

    except pymongo.errors.OperationFailure as e:
        print(f"MongoDB authentication error: {e}")
        return _handle_mongo_error("Database authentication failed. Check MongoDB Atlas credentials.")
    except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.NetworkTimeout) as e:
        return _handle_mongo_error(str(e))
    except Exception as e:
        print(f"History retrieval error: {repr(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def chatbot_clear_history_view(request):
    """Clear user's chat history"""
    try:
        user_doc = _get_user_from_token(request)
        if not user_doc:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return _handle_mongo_error(str(e))

    try:
        username = user_doc["_id"]
        result = chats_collection.delete_many({"username": username})

        return Response({
            "message": f"Deleted {result.deleted_count} chat entries",
            "deleted_count": result.deleted_count
        }, status=status.HTTP_200_OK)

    except pymongo.errors.OperationFailure as e:
        print(f"MongoDB authentication error: {e}")
        return _handle_mongo_error("Database authentication failed. Check MongoDB Atlas credentials.")
    except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.NetworkTimeout) as e:
        return _handle_mongo_error(str(e))
    except Exception as e:
        print(f"Clear history error: {repr(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)