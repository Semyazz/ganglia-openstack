from distutils.core import setup
from glob import glob

setup(
    name='ganglia-zeromq',
    version='0.1',
    packages=['plugin'],
    url='',
    license='',
    author='Szymon G.',
    author_email='',
    description='Ganglia metrics publisher through JsonRPC ZeroMQ',
    data_files=[
            ('/etc/ganglia', ['gmetad-python.conf']),
            ('/usr/local/lib64/ganglia/python_modules/gmetad', glob('plugin/*plugin.py'))]
)
