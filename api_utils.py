import requests

gfg_url = 'https://ide.geeksforgeeks.org'
api_url = f"{gfg_url}/main.php"


def execute_code(code_string):
    data = {
        'lang': 'python3',
        'code': code_string,
        'input': '',
        'save': True
    }

    print("Code Input to API:", code_string)
    response = requests.post(api_url, data=data)
    response_data = response.json()
    response_data['code_url'] = f"{gfg_url}/{response_data.pop('id')}"
    response_data['has_compilation_error'] = len(response_data.pop('cmpError')) > 0
    response_data['has_run_time_error'] = len(response_data.pop('rntError')) > 0

    response_data.pop('hash')
    response_data.pop('lxcOutput')

    return response_data


if __name__ == '__main__':
    code = input("Write Code to Execute:\n")
    print(execute_code(code))
