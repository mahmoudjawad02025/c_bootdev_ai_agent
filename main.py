import os
from openai import OpenAI
from dotenv import load_dotenv
import argparse
from prompts import system_prompt
from call_function import available_functions
import json
from call_function import call_function1
#MahmoudAbuAlsebaa

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key is None :
    raise RuntimeError("api_key is None !")


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def send_request(messages):
    return client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=0,
        tools=available_functions,
    )

def main():
    print("1 - - - - - - - - - - - \n")
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt}
    ]

    print("2 - - - - - - - - - - - \n")
    
    for _ in range(20):
        response = send_request(messages)
        message = response.choices[0].message
        messages.append(message)
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                # print(f"Calling function: {tool_call.function.name}({function_args})")
                result_message = call_function1(tool_call, args.verbose)
                messages.append(result_message)
                if(args.verbose): print(f"-> {result_message['content']}")
                if len(result_message['content']) == 0:
                    raise Exception("Tool message content is empty")
        else:
            if args.verbose:
                print(f"User prompt: {args.user_prompt}\n")
                print(f"Prompt tokens: {response.usage.prompt_tokens}\n")
                print(f"Response tokens: {response.usage.completion_tokens}")
            print(message.content)
            return
        
    if message.tool_calls:
        print("Error: Max iterations reached")
        exit(1)
        
            

    # print("3 - - - - - - - - - - - \n")
    # if response.usage is None :
    #     raise RuntimeError("response.usage is None")



    # print("4 - - - - - - - - - - - \n")
    # if not message.tool_calls:
    #     if(not args.verbose):
    #         print(response.choices[0].message.content)
    #     else:
    #         print(f"User prompt: {args.user_prompt}\n")
    #         print(f"Prompt tokens: {response.usage.prompt_tokens}\n")
    #         print(f"Response tokens: {response.usage.completion_tokens}")


if __name__ == "__main__":
    main()
