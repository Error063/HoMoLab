import os
import zipfile
from homo.lab.__main__ import version

os.system('python setup.py bdist_wheel')
print('first build wheel finished, repacking resources...')
dir_list = os.listdir('dist')
file_name = ''
for file in dir_list:
    if version in file.split('-') and file.endswith('.whl') and file.startswith('HoMoLab'):
        file_name = file
        break
file_path = os.path.abspath(os.path.join('.', 'dist', file_name))
with zipfile.ZipFile(file_path, mode='a') as f:
    for i in os.walk(os.path.join('.', 'homo', 'resources')):
        for n in i[2]:
            f.write(''.join((i[0], '\\', n)))
    for i in os.walk(os.path.join('.', 'homo', 'theme')):
        for n in i[2]:
            f.write(''.join((i[0], '\\', n)))
print('repack wheel finished, uploading to pypi')
os.system(f'twine upload ./dist/{file_name}')