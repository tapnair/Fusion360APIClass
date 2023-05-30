import json
import multiprocessing as mp
import os
import subprocess
import sys
import traceback

import adsk.cam
import adsk.core
import adsk.fusion
from .api_client.api_client import start, get_chat_completion

APP_PATH = os.path.dirname(os.path.abspath(__file__))

app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    try:
        prompt = 'Ask your question'
        title = 'OpenAI Chat Demo'
        default_value = 'Tell me about Fusion 360'
        (user_input_text, cancelled) = ui.inputBox(prompt, title, default_value)
        if cancelled:
            return

        # api_response = get_chat_completion(user_input_text)

        # mp.set_start_method('spawn')
        # py_path = os.path.join(sys.exec_prefix, 'bin', 'python')
        py_path = os.path.join(sys.exec_prefix, 'bin')
        # py_path = os.path.join(sys.exec_prefix, 'Python')
        log('New Path:')
        log(py_path)

        log('Process Started')
        # parent_conn.send(user_input_text)
        # completed = subprocess.run(['./venv/bin/python', './api_client/api_client.py'], capture_output=True)

        py_exec = '/Library/Frameworks/Python.framework/Versions/3.9/bin'
        app_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_client', 'api_client.py')
        new_env = {'PATH': py_exec}

        completed = subprocess.run(['python3', app_file, user_input_text], capture_output=True, timeout=60, env=new_env)

        api_response = json.loads(completed.stdout.decode('utf-8'))

        log('stdout:\n' + completed.stdout.decode('utf-8'))
        log('stderr:\n' + completed.stderr.decode('utf-8'))
        # api_response = get_chat_completion(user_input_text)

        msg = api_response.get('msg', 'No Message')
        title = 'OpenAI Chat Response'
        button_type = adsk.core.MessageBoxButtonTypes.OKButtonType
        icon_type = adsk.core.MessageBoxIconTypes.InformationIconType
        ui.messageBox(msg, title, button_type, icon_type)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def handle_error(msg):
    log_type = adsk.core.LogTypes.ConsoleLogType
    log_level = adsk.core.LogLevels.ErrorLogLevel
    app.log(msg, log_level, log_type)


def log(msg):
    log_type = adsk.core.LogTypes.ConsoleLogType
    log_level = adsk.core.LogLevels.InfoLogLevel
    app.log(msg, log_level, log_type)
    adsk.doEvents()
