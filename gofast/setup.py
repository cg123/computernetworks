from distutils.core import setup

import gpio

setup(name='gofast',
    author='Charles Goddard',
    author_email='chargoddard@gmail.com',
    ext_modules=[gpio.ffi.verifier.get_extension()])
