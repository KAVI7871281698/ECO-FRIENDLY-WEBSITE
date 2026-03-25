import google.generativeai as genai
import os

api_key = "AIzaSyC_icsHbFv0gzrzInXihC_vGXNReUuv_aI"
genai.configure(api_key=api_key)

try:
    models = [m.name for m in genai.list_models()]
    with open("avail_models.txt", "w") as f:
        f.write("\n".join(models))
    print("DONE")
except Exception as e:
    with open("avail_models.txt", "w") as f:
        f.write(str(e))
    print("ERROR")
