import json
from openai import OpenAI
from PIL import Image
import base64
import io
import os
from fc_chatbot import Chatbot
def resize_image_in_memory(input_data, size=(512, 512)):
    # Create an in-memory stream for the input data
    input_stream = io.BytesIO(input_data)

    # Open the image from the in-memory stream
    with Image.open(input_stream) as img:
        # Resize the image
        resized_img = img.resize(size)

        # Create an in-memory stream for the resized image
        output_stream = io.BytesIO()

        # Save the resized image to the in-memory stream
        resized_img.save(output_stream, format="JPEG")

        # Get the bytes of the resized image
        resized_data = output_stream.getvalue()

        return resized_data
def image_to_base64(image_data):
    # Encode the image data as base64
    base64_string = base64.b64encode(image_data).decode("utf-8")

    return base64_string
def LoadAndProcessImage(input_image_path):
    with open(input_image_path, "rb") as img_file:
        input_image_data = img_file.read()
    # Resize the image in-memory
    resized_image_data = resize_image_in_memory(input_image_data)

    # Convert the resized image to base64 string
    base64_string = image_to_base64(resized_image_data)
    return base64_string

apiKey = "<your api key>"
client = OpenAI(api_key=apiKey)

def loadimage(path):
    return "data:image/jpeg;base64,"+LoadAndProcessImage(path)
def listfiles():
    folder_path = "./"
    jpeg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")]
    output = ""
    for file in jpeg_files:
        output += f"{file},"
    jpeg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpeg")]
    for file in jpeg_files:
        output += f"{file},"
    return output
sysprompt = "You are a helpful assistant."
chat = Chatbot(sysprompt)
chat.addFunction(loadimage,"loadimage","image",["path"])
chat.addFunction(listfiles,"list all jpg files","text",[])
chat.init()
while True:
    prompt = input("user: ")
    output = chat.chat(prompt,client)
    print(f"AI: {output}")