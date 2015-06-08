# -*- coding: utf-8 -*-

# python setup.py build
# python setup.py bdist_msi

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

# options = {
#     'build_exe': {
#         'includes': 'atexit'
#     }
# }

executables = [
    Executable('PYQT5GUI.py', base=base)
]

setup(name='三种方法',
      version='0.1',
      description='获取豆瓣图书数据的三种方法',
      # options=options,
      executables=executables
      )
