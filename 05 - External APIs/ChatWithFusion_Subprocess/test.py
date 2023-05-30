import subprocess

# def run(user_input_text):
#     # py_path = os.path.join(sys.exec_prefix, 'bin', 'python')
#     py_path = os.path.join(sys.exec_prefix, 'python')
#
#     subprocess.run(['python3', './api_client/api_client.py'], shell=True, check=True, capture_output=True)
#     print('Done')


if __name__ == '__main__':
    print('Start')
    # subprocess.run(['python3', '-m', 'venv', 'venv'])
    # subprocess.run(['source venv/bin/activate'])
    # subprocess.run(['.', 'venv/bin/activate', 'venv'], shell=True)
    # subprocess.run(['./venv/bin/pip', 'install', 'requests'])
    # cmd = ['./venv/bin/pip', 'install', 'requests']
    # subprocess.run(cmd)
    # subprocess.run(cmd, capture_output=True, shell=True)
    subprocess.run(['python3', './api_client/api_client.py'])
    print('Done')
