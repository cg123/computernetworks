from distutils.core import setup

import gofast.gpio

setup(name='gofast',
    author='Charles Goddard',
    author_email='chargoddard@gmail.com',
    packages=['gofast'],
    ext_package='gofast',
    ext_modules=[gofast.gpio.ffi.verifier.get_extension()])
