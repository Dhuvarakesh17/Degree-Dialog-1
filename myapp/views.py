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
            model = genai.GenerativeModel("models/gemini-2.0-flash")
            
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