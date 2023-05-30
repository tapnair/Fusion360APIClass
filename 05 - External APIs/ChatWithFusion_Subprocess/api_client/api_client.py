import json
import os
import sys
import traceback


# For this to work it is assumed that you have done the following:
# 1. Open a shell or terminal
# 2. Navigate to this directory: ".../Fusion360APIClass/05 - External APIs/ChatWithFusion_Subprocess/api_client"
# 3. Installed the openai sdk:  pip3 install -t lib --upgrade openai

def get_chat_completion(user_input_text):

    # Get the path to the local folder and the lib folder and add to sys path
    app_path = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(app_path, 'lib')
    sys.path.insert(0, app_path)
    sys.path.insert(0, lib_path)

    import openai
    import open_ai_key
    openai.api_key = open_ai_key.open_ai_key

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": user_input_text
            }]
        )
        return json.dumps({
            'status': 'SUCCESS',
            'msg': completion.choices[0].message.content
        })

    except:
        name = 'Get Chat Completion - API Request'
        return json.dumps({
            'status': 'FAILED',
            'msg': f'{name}\n{traceback.format_exc()}'
        })


def start(msg):
    response = get_chat_completion(msg)

    # Response is just printed to stdout
    print(response)


if __name__ == '__main__':
    start(sys.argv[1])
