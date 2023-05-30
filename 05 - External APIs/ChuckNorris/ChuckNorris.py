
import os
import sys
import importlib
import traceback

import adsk.cam
import adsk.core
import adsk.fusion


from contextlib import ContextDecorator
from os.path import dirname, abspath

SCRIPT_DIRECTORY = dirname(abspath(__file__))

app = adsk.core.Application.get()
ui = app.userInterface

# For this to work it is assumed that you have done the following:
# 1. Open a shell or terminal
# 2. Navigate to this directory: ".../Fusion360APIClass/05 - External APIs/ChatWithFusion_Subprocess/api_client"
# 3. Installed the requests library:  pip3 install -t lib --upgrade requests


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


@lib_import(SCRIPT_DIRECTORY)
def make_request(url, headers=None):
    import requests
    importlib.reload(requests)
    r = requests.get(url, headers=headers)
    return r


def run(context):
    try:
        r = make_request('https://api.chucknorris.io/jokes/random')

        r_json = r.json()
        joke = r_json['value']

        title = 'Chuck Norris Fact'
        button_type = adsk.core.MessageBoxButtonTypes.OKButtonType
        icon_type = adsk.core.MessageBoxIconTypes.InformationIconType
        ui.messageBox(joke, title, button_type, icon_type)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
