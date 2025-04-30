# import google.generativeai as genai
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import os
# from fuzzywuzzy import fuzz

# # Load API key
# API_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=API_KEY)

# # List of college-related keywords
# COLLEGE_KEYWORDS = [
#     "college", "university", "admission", "degree", "scholarship", "course", 
#     "faculty", "campus", "higher education", "tuition", "student","institution","institute","IIT","NIT","IIIT","IIM"
# ]

# # List of general greetings
# GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

# def is_college_related(message):
#     """Check if the message is related to college topics, allowing for minor typos."""
#     for keyword in COLLEGE_KEYWORDS:
#         if fuzz.partial_ratio(keyword, message) > 80:
#             return True
#     return False

# @csrf_exempt    
# def chatbot_view(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_message = data.get("message", "").lower()

#         # Handle greetings
#         if any(greet in user_message for greet in GREETINGS):
#             return JsonResponse({"response": "Hello! How can I assist you today?"})

#         # Check if the message is college-related
#         if not is_college_related(user_message):
#             return JsonResponse({"response": "I'm here to assist with college-related inquiries only."})

#         try:
#             # Use a valid Gemini model
#             model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
#             response = model.generate_content(user_message)

#             bot_reply = response.text if response.text else "Sorry, I couldn't process that."

#             return JsonResponse({"response": bot_reply})

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     return JsonResponse({"error": "Invalid request"}, status=400)
import google.generativeai as genai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from fuzzywuzzy import fuzz

# Load API key
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

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
def chatbot_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"response": "Please type your question about college or higher education."})

        try:
            # Initialize the Gemini model with the college advisor persona
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            
            # Start a chat session with the system instruction
            chat = model.start_chat()
            
            # Send both the system prompt and user message
            response = chat.send_message(
                f"{COLLEGE_ADVISOR_PROMPT}\n\nUser question: {user_message}"
            )

            bot_reply = response.text if response.text else "I'm not sure how to answer that. Could you provide more details about your college-related question?"

            return JsonResponse({"response": bot_reply})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)