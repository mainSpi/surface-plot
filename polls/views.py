from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

from pprint import pprint

import matplotlib.pyplot as plt
from matplotlib import cm
# from matplotlib.ticker import LinearLocator
from matplotlib.ticker import MultipleLocator
import numpy as np
from PIL import Image
# from numpy.lib.shape_base import vsplit

import base64
from io import BytesIO

from django.shortcuts import redirect
from django.template.response import TemplateResponse

import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image
from io import BytesIO

port = 465
password = "Oi112466"
context = ssl.create_default_context()
mail = "meuraspinfo@gmail.com"

types = ['image/jpeg', 'image/png', 'image/tiff', 'image/webp', 'image/gif', 'image/x-icon', 'image/bmp']

def bunda(request):
    string = request.session['b64']

    img     = decodeImage(string)
    img_byte_arr = getBytesFromImage(img)

    resp = HttpResponse(img_byte_arr, content_type="image/jpeg")
    prepareResponse(resp)
    return resp

    # if ('show' in request.session and request.session['show'] == 'True'):
    #     print('entrei pra mostrar imagem, show: '+request.session['show'])
    #     request.session['show'] = 'False'
    #     print('acabei de mudar agora deve estar: '+request.session['show'])
    #     string = request.session['b64']
    #     img = decodeImage(string)
    #     img_byte_arr = getBytesFromImage(img)
    #     resp = HttpResponse(img_byte_arr, content_type="image/jpeg")
    #     prepareResponse(resp)
    #     return resp
    # else:
    #     print('nao entrei, mostrando site normal')
    #     resp = redirect('/')
    #     prepareResponse(resp)
    #     return resp


def cu(request):
    if request.method == 'POST':
        file = request.FILES['image']

        if file.size > 50 * 1000000:
            messages.error(request,    'A imagem deve ser menor que 50 Mb. Tente novamente.')            
        elif file.content_type not in types:
            messages.error(request,    'O arquivo deve ser uma imagem. Tente novamente.')
        else:
            img = image_treatment(file.file)

            string = encodeImage(img)

            sendEmail([Image.open(file.file),img])

            request.session['b64'] = string

            args = {}
            args['b64'] = string
            resp = TemplateResponse(request, 'site/index.html', args)
            prepareResponse(resp)

            return resp
    else:
        resp = render(request, 'site/index.html')
        prepareResponse(resp)
        return resp

def sendEmail(array):
    message = MIMEMultipart()
    message["From"] = mail
    message["To"] = mail
    message["Subject"] = "Log"

    for img in array:
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        part = MIMEBase("application", "octet-stream")
        part.set_payload(img_byte_arr)
        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            "attachment; filename=img.jpeg",
        )
        message.attach(part)

    text = message.as_string()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(mail, password)
        server.sendmail(mail, mail, text)

def encodeImage(img):
    im_file = BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    im_b64 = base64.b64encode(im_bytes)
    return im_b64.decode('utf-8')

def prepareResponse(resp):
    resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp['Pragma'] = 'no-cache'

def getBytesFromImage(img):
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='jpeg')
    return img_byte_arr.getvalue()

def decodeImage(string):
    im_bytes = base64.b64decode(string)   # im_bytes is a binary image
    im_file = BytesIO(im_bytes)  # convert image to file-like object
    return Image.open(im_file)   # img is now PIL Image object


def image_treatment(bts):
    
    # magic_number = int(input("enter the magic number: "))  # should be 200 for semless surface
    magic_number = 100

    bts.seek(0)
    im = Image.open(bts)

    width = im.size[0]
    height = im.size[1]

    im = im.convert("L")

    def fun(x, y):
        a = []
        for h in range(0, height):
            for w in range(0, width):
                a.append(im.getpixel((w, h)))
        return np.array(a)


    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    # Make data.
    X = []
    Y = []

    for w in range(0, width):
        X.append(w)

    for h in range(0, height):
        Y.append(h)


    X, Y = np.meshgrid(X, Y)

    zs = np.array(fun(np.ravel(X), np.ravel(Y)))
    Z = zs.reshape(X.shape)

    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, rstride=int(width/magic_number), cstride=int(height/magic_number), cmap="turbo" )

    # cset = ax.contourf(X, Y, Z, zdir='z', offset=-100, cmap=cm.coolwarm)

    # fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1)

    ax.set_zlim(0, 255)
    ax.set_zlabel("depth")
    ax.zaxis.set_major_locator(MultipleLocator(100))

    ax.set_xlim(0, width)
    ax.xaxis.set_major_locator(MultipleLocator(100))

    ax.set_ylim(0, height)
    ax.yaxis.set_major_locator(MultipleLocator(100))

    plt.axis('off')
    plt.xlabel('w')
    plt.ylabel('h')

    plt.subplots_adjust(
        top=1.0,
        bottom=0.0,
        left=0.0,
        right=1.0,
        hspace=0.2,
        wspace=0.2
    )

    # plt.savefig('1.png', bbox_inches='tight', dpi=200)  # , pad_inches = 0

    print("Doing it...")
    def fig2img(fig):
        buf = BytesIO()
        fig.savefig(buf,bbox_inches='tight', dpi=200)
        buf.seek(0)
        img = Image.open(buf)
        return img

    aaa = []

    ax.azim = 90 
    ax.elev = 66
    aaa.append(fig2img(fig))

    ax.azim = 134# 54 
    ax.elev = 50
    aaa.append(fig2img(fig))

    ax.azim = -134 
    ax.elev = 50
    aaa.append(fig2img(fig))

    ax.azim = 54 
    ax.elev = 50
    aaa.append(fig2img(fig))

    # ax.azim = 90 
    # ax.elev = 0
    # aaa.append(fig2img(fig))

    ax.azim = 90 
    ax.elev = 90
    aaa.append(fig2img(fig))

    w = aaa[1].size[0]
    h = aaa[1].size[1]

    aaa.insert(0,im.resize((w,h)))

    def create_collage(width, height, listofimages):
        cols = 3
        rows = 2
        thumbnail_width = width//cols
        thumbnail_height = height//rows
        size = thumbnail_width, thumbnail_height
        new_im = Image.new('RGB', (width, height))
        ims = []
        for p in listofimages:
            # img = Image.open(p)
            p.thumbnail(size)
            ims.append(p)
        i = 0
        x = 0
        y = 0
        for col in range(cols):
            for row in range(rows):
                # print(i, x, y)
                new_im.paste(ims[i], (x, y))
                i += 1
                y += thumbnail_height
            x += thumbnail_width
            y = 0

        # name_list = filename.split('/')
        # name = ''

        # for s in range(0,len(name_list)-1):
            # name += name_list[s]
            # name += '/'
        
        # name += 'Collage.jpg'

        # new_im.save(name)
        return new_im


    return create_collage(w*3, h*2, aaa)