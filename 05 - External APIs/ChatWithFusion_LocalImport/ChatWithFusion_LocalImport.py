import importlib
import os
import sys
import traceback
from contextlib import ContextDecorator

import adsk.cam
import adsk.core
import adsk.fusion

from .open_ai_key import open_ai_key


app = adsk.core.Application.get()
ui = app.userInterface

# For this to work it is assumed that you have done the following:
# 1. Open a shell or terminal
# 2. Navigate to this directory: ".../Fusion360APIClass/05 - External APIs/ChatWithFusion_LocalImport"
# 3. Installed the openai sdk:  pip3 install -t lib --upgrade openai


def run(context):
    try:
        prompt = 'Ask your question'
        title = 'OpenAI Chat Demo'
        default_value = 'Tell me about Fusion 360'
        (user_input_text, cancelled) = ui.inputBox(prompt, title, default_value)
        if cancelled:
            return

        app.log('About to call OpenAI API')

        api_response = get_chat_completion(user_input_text)

        title = 'OpenAI Chat Response'
        button_type = adsk.core.MessageBoxButtonTypes.OKButtonType
        icon_type = adsk.core.MessageBoxIconTypes.InformationIconType
        ui.messageBox(api_response, title, button_type, icon_type)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


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

    def __enter__(self):
        self.path = os.path.join(self.app_path, self.library_folder)
        sys.path.insert(0, self.path)
        return self

    def __exit__(self, *exc):
        if self.path in sys.path:
            sys.path.remove(self.path)
        return False


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


@lib_import(SCRIPT_DIRECTORY, library_folder='lib')
def get_chat_completion(user_input_text):
    import openai
    importlib.reload(openai)

    openai.api_key = open_ai_key

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": user_input_text
            }]
        )
        return completion.choices[0].message.content

    except:
        handle_error('Get Image Variations - API Request')
        return 'Failed'


def handle_error(name):
    log_type = adsk.core.LogTypes.ConsoleLogType
    log_level = adsk.core.LogLevels.ErrorLogLevel
    app.log(f'{name}\n{traceback.format_exc()}', log_level, log_type)
