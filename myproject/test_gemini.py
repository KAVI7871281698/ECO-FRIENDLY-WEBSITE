import os
import google.generativeai as genai

api_key = "AIzaSyC_icsHbFv0gzrzInXihC_vGXNReUuv_aI"
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print("ERROR")
    print(str(e))
