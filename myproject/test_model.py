import google.generativeai as genai
import os

api_key = "AIzaSyC_icsHbFv0gzrzInXihC_vGXNReUuv_aI"
genai.configure(api_key=api_key)

try:
    # Try the most likely stable name
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Say 'hello' in one word")
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print("ERROR")
    print(str(e))
