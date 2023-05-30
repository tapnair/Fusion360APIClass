import json
import os
import subprocess
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

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

        log('Running Subprocess to call OpenAI API')

        py_dir = '/Library/Frameworks/Python.framework/Versions/3.9/bin'
        client_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_client', '')
        client_file = os.path.join(client_dir, 'api_client.py')
        new_env = {'PATH': py_dir}

        completed = subprocess.run(['python3', client_file, user_input_text],
                                   capture_output=True, timeout=60, env=new_env)

        log(' Subprocess output:')
        log('stdout:\n' + completed.stdout.decode('utf-8'))
        log('stderr:\n' + completed.stderr.decode('utf-8'))

        # Read response from stdout
        # the subprocess simply prints the response as a json string
        api_response = json.loads(completed.stdout.decode('utf-8'))
        msg = api_response.get('msg', 'No Message')

        title = 'OpenAI Chat Response'
        button_type = adsk.core.MessageBoxButtonTypes.OKButtonType
        icon_type = adsk.core.MessageBoxIconTypes.InformationIconType
        ui.messageBox(msg, title, button_type, icon_type)

    except:
        handle_error('Failed:\n{}'.format(traceback.format_exc()))


def handle_error(msg):
    log_type = adsk.core.LogTypes.ConsoleLogType
    log_level = adsk.core.LogLevels.ErrorLogLevel
    app.log(msg, log_level, log_type)


def log(msg):
    log_type = adsk.core.LogTypes.ConsoleLogType
    log_level = adsk.core.LogLevels.InfoLogLevel
    app.log(msg, log_level, log_type)
    adsk.doEvents()
