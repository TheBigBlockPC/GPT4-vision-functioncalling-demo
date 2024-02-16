import json
from openai import OpenAI
from PIL import Image
import base64
import io
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
functions = "\"loadimage\" it takes in the input \"path\""
sysprompt = "You are a helpful assistant.you have the functionss "+functions+". If you use a function use a function begin the message with \"function:\" and then a Jain string formatted like this : {\"name\":\"<function name>\",\"args\":[<the arguments the function uses>]} the user's response to your function request is the return value if the function. strictly follow the provided json format. Never correct the response of the function"

chatlog = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": sysprompt,
            },
        ]
    }
]
def loadimage(path):
    return "data:image/jpeg;base64,"+LoadAndProcessImage(path)
def runFunction(functionCall):
    print(functionCall)
    functions = {"loadimage":{"function":loadimage,"type":"image"}}
    functionName = functionCall["name"]
    call = functions[functionName]
    output = call["function"](*(functionCall["args"]))
    if call["type"] == "text":
        return {
                "type": "text",
                "text": str(output),
            }
    else:
        return {
                "type": "image_url",
                "image_url": {
                    "url":output
                }
            }
def Generate(input):
    chatlog.append({
        "role": "user",
        "content": [
            input
        ]
    })
    response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=chatlog,
    max_tokens=300,
    )
    text:str = response.choices[0].message.content
    chatlog.append({
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": text,
            },
        ]
    })
    if text.startswith("function:"):
        data = text.split("function:")[1]
        data = json.loads(data)
        result = runFunction(data)
        return Generate(result)
    return text
while True:
    prompt = input("user: ")
    data = {
        "type": "text",
        "text": prompt,
    }
    output = Generate(data)
    print(f"AI: {output}")