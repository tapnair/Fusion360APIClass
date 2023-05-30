import json
import os
import sys
import traceback
from contextlib import ContextDecorator


from open_ai_key import open_ai_key

APP_PATH = os.path.dirname(os.path.abspath(__file__))


class lib_import(ContextDecorator):
    """The lib_import class is a wrapper class to allow temporary import of a local library directory

            By default, it assumes there is a folder named 'lib' in the add-in root directory.

            First install a 3rd party library (such as requests) to this directory.

            .. code-block:: bash

                # Assuming you are in the add-in root directory (sudo may not be required...)
                sudo python3 -m pip install -t ./lib requests

            Then you can temporarily import the library before making a call to the requests function.
            To do this use the *@lib_import(...)* decorator on a function that uses the library.

            Here is an example function for using `Requests <https://requests.readthedocs.io/en/master/>`_:

            .. code-block:: python

                @lib_import(APP_PATH)
                def make_request(url, headers=None):
                    import requests
                    r = requests.get(url, headers=headers)
                    return r

            Args:
                app_path(str): The root path of the addin.  Should be dynamically calculated.
                library_folder(:obj:`str`, optional): Library folder name (relative to app root). Defaults to 'lib'
            """

    def __init__(self, app_path, library_folder='lib'):
        super().__init__()
        self.path = ''
        self.app_path = app_path
        self.library_folder = library_folder
        # self.py_path = os.path.join(sys.exec_prefix, 'lib', 'python3.9')
        # self.py_path = os.path.join(sys.exec_prefix, 'lib')
        self.py_path = sys.exec_prefix
        self.other_path = os.path.join(self.path, 'OpenSSL')

    def __enter__(self):
        self.path = os.path.join(self.app_path, self.library_folder)
        sys.path.insert(0, self.path)
        # sys.path.insert(0, self.py_path)
        # print(sys.path)
        return self

    def __exit__(self, *exc):
        if self.path in sys.path:
            sys.path.remove(self.path)
        # if self.py_path in sys.path:
        #     sys.path.remove(self.py_path)
        if self.other_path in sys.path:
            sys.path.remove(self.other_path)
        return False


# @lib_import(APP_PATH, library_folder='lib')
def get_chat_completion(user_input_text):
    app_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(app_path, 'lib')
    sys.path.insert(0, path)
    import openai
    openai.api_key = open_ai_key
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


# def start(child_conn, user_input_text, log):
def start(msg):
    # print(f'I am here.\n    Running main in api_client.py')
    # print(f'User Message:\n    {msg}')
    response = get_chat_completion(msg)
    # print(f'Response:\n{response.get("msg", "No response")}')
    # response.get("msg", "No response")
    print(response)


if __name__ == '__main__':
    # start('Tell me about Fusion 360')
    # print(sys.path)
    start(sys.argv[1])
