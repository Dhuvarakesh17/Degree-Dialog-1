import google.generativeai as genai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from fuzzywuzzy import fuzz

# Load API key
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# List of college-related keywords
COLLEGE_KEYWORDS = [
    "college", "university", "admission", "degree", "scholarship", "course", 
    "faculty", "campus", "higher education", "tuition", "student","institution","institute","IIT","NIT","IIIT","IIM"
]

# List of general greetings
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

def is_college_related(message):
    """Check if the message is related to college topics, allowing for minor typos."""
    for keyword in COLLEGE_KEYWORDS:
        if fuzz.partial_ratio(keyword, message) > 80:
            return True
    return False

@csrf_exempt    
def chatbot_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "").lower()

        # Handle greetings
        if any(greet in user_message for greet in GREETINGS):
            return JsonResponse({"response": "Hello! How can I assist you today?"})

        # Check if the message is college-related
        if not is_college_related(user_message):
            return JsonResponse({"response": "I'm here to assist with college-related inquiries only."})

        try:
            # Use a valid Gemini model
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            response = model.generate_content(user_message)

            bot_reply = response.text if response.text else "Sorry, I couldn't process that."

            return JsonResponse({"response": bot_reply})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
