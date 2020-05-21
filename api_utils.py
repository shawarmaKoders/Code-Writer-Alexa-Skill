import sys
from io import StringIO
import contextlib
import requests


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def execute_code(code_string):
    res = requests.post(url='https://hastebin.com/documents', data=code_string)
    paste = f"https://hastebin.com/{res.json()['key']}"
    with stdoutIO() as s:
        try:
            exec(code_string)
        except:
            print('ERROR_Z')

    return s.getvalue().strip(), paste


if __name__ == '__main__':
    code = input("Write Code to Execute:\n")
    print(execute_code(code))
