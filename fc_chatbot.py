from openai import OpenAI
import json
class Chatbot():
    _sysprompt = ""
    _provided_sysprompt = ""
    _functions = {}
    _function_objects = []
    chatlog = []
    def __init__(self,sysprompt):
        self._sysprompt = sysprompt
        self._provided_sysprompt = sysprompt
    def addFunction(self,function,name,returns,args):
        self._functions[name] = {
            "function":function,
            "type":returns
        }
        f = self._function(name,args)
        self._function_objects.append(f)
    def init(self):
        self._sysprompt = self._updateSysprompt(self._provided_sysprompt,self._function_objects)
        self.chatlog = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self._sysprompt,
                    },
                ]
            }
        ]
    def chat(self,prompt,client):
        data = {
            "type": "text",
            "text": prompt,
        }
        return self._Generate(data,client)
    def _runFunction(self,functionCall):
        functionName = functionCall["name"]
        call = self._functions[functionName]
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
    def _Generate(self,inp,client):
        self.chatlog.append({
            "role": "user",
            "content": [
                inp
            ]
        })
        response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=self.chatlog,
        max_tokens=300,
        )
        text:str = response.choices[0].message.content
        self.chatlog.append({
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
            result = self._runFunction(data)

            return self._Generate(result,client)
        return text
    class _function():
        name = ""
        args = []
        func = None
        def __init__(self,name,args):
            self.name = name
            self.args = args
    def _updateSysprompt(self,sysprompt,functions:list[_function]):
        functions_str = ""
        for i in functions:
            functions_str += f"(\"{i.name}\""
            if len(i.args) != 0:
                functions_str += " it takes in the "
                if len(i.args) == 1:
                    functions_str += "input "
                else:
                    functions_str += "inputs "
                for i2 in i.args:
                    functions_str += f"\"{i2}\","
            functions_str += "),"
        sysprompt = f"{sysprompt} you have the functions "+functions_str+". If you use a function use a function begin the message with \"function:\" and then a Jain string formatted like this : {\"name\":\"<function name>\",\"args\":[<the arguments the function uses>]} the user's response to your function request is the return value if the function. strictly follow the provided json format. Never correct the response of the function"
        return sysprompt