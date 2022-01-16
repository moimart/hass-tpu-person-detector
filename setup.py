from setuptools import setup

setup(name='hass-jetson-person-detector',
      version='0.1',
      description='A person detector that takes a video source, publishes an rtstp stream and exposes an occupancy sensor to homeassistant',
      url='https://github.com/moimart/hass-jetson-person-detector',
      author='Moises Martinez',
      author_email='moises@martinez.sh',
      license='MIT',
      packages=['hass-jetson-person-detector'],
      install_requires=[
          'ffmpeg-python',
          'numpy',
          'pillow',
          'paho-mqtt'
      ],
      zip_safe=False)