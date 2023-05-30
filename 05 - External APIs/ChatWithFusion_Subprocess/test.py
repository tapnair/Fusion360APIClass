import json

from api_client.api_client import get_chat_completion


# Use this test file to test what will be run in the subprocess
# Run this file directly in your IDE or python shell, not through Fusion scripts.
# It can be difficult to debug what is happening in the subprocess otherwise.

TEST_PROMPT = 'Tell me about Fusion 360'


if __name__ == '__main__':
    print('Start')
    print('Requesting Chat completion with prompt:')
    print(TEST_PROMPT)
    print('This may take a minute...')

    response_string = get_chat_completion(TEST_PROMPT)
    response = json.loads(response_string)
    msg = response.get('msg', 'No Message in response')
    status = response.get('status', 'No Status in response')

    print('Results')
    print(f'Status: {status}')
    print('API Response:')
    print(msg)
    print('Done')
