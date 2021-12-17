# surface-plot

Surface-plot is a python-powered, django web application. Using matplotlib and opencv, this app scans photos for faces and generates a 3d mesh from them.

## Examples

- ![one](https://github.com/mainSpi/surface-plot/blob/main/demo/1.png?raw=true)
- ![two](https://github.com/mainSpi/surface-plot/blob/main/demo/2.png?raw=true)


## Features

- Face recognition with openCV cascade classifier.
- Minimalist front-end, supporting drag-and-drop and simple image uploading.
- 3d surface plotting and visualization, using matplotlib and numpy.

## Testing

This app is currently deployed at [heroku](https://django-surface-plot.herokuapp.com/)

## Try it yourself

1. First, replace the environment  variable ```SECRET_KEY = os.environ['secret_key']``` at [``` /surface/settings.py ```](https://github.com/mainSpi/surface-plot/blob/main/surface/settings.py).
It should be set to your own django secret key, which can be generated in [this site](https://djecrety.ir/)


2. Then clone the repo and run it as any other django app:
``` $ python manage.py runserver ```

3. Done!
