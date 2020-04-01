import os
import platform
from shutil import copyfile, make_archive

linux_site_packages = ['venv', 'lib', 'python3.6', 'site-packages']
windows_site_packages = ['venv', 'Lib', 'site-packages']

site_packages = linux_site_packages
if platform.system() == 'Windows':
	site_packages = windows_site_packages

site_packages_path = os.path.join(*site_packages)

copyfile('alexa.py', f'{site_packages_path}/alexa.py')
copyfile('lambda_function.py', f'{site_packages_path}/lambda_function.py')
copyfile('api_utils.py', f'{site_packages_path}/api_utils.py')
make_archive('lambda_function', 'zip', site_packages_path)
