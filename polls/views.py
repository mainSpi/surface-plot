from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.template.response import TemplateResponse
# from django.shortcuts import redirect

from pprint import pprint
from PIL import Image
import base64
from io import BytesIO

import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import ImageOps
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MultipleLocator
import numpy as np

types = ['image/jpeg', 'image/png', 'image/tiff', 'image/webp', 'image/gif', 'image/x-icon', 'image/bmp']

def bunda(request):
	string = request.session['b64']

	img     = decodeImage(string)
	img_byte_arr = getBytesFromImage(img)

	resp = HttpResponse(img_byte_arr, content_type="image/jpeg")
	prepareResponse(resp)
	return resp


def cu(request):
	if request.method == 'POST':
		file = request.FILES.get('image')

		if file.size > 50 * 1000000:
			messages.error(request,    'A imagem deve ser menor que 50 Mb. Tente novamente.')            
		elif file.content_type not in types:
			messages.error(request,    'O arquivo deve ser uma imagem. Tente novamente.')
		else:
			raw_img = open_image(file.file)
			img = image_treatment(raw_img)

			string = encodeImage(img)

			sendEmail((raw_img,img))

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

def open_image(bts):
	bts.seek(0)
	im = Image.open(bts)
	im = ImageOps.exif_transpose(im)
	im = im.convert('RGB')
	return im

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

	

def image_treatment(im):
	
	magic_number = 7

	im = im.resize((1000,1000))

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

	surf = ax.plot_surface(X, Y, Z, rstride=magic_number, cstride=magic_number, cmap="turbo" )

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

	print("Doing it...")
	def fig2img(fig):
		buf = BytesIO()
		fig.savefig(buf,bbox_inches='tight', dpi=200)
		buf.seek(0)
		img = Image.open(buf)
		return img.transpose(Image.FLIP_LEFT_RIGHT)

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
			p.thumbnail(size)
			ims.append(p)
		i = 0
		x = 0
		y = 0
		for col in range(cols):
			for row in range(rows):
				new_im.paste(ims[i], (x, y))
				i += 1
				y += thumbnail_height
			x += thumbnail_width
			y = 0

		return new_im

	return create_collage(w*3, h*2, aaa)


port = 465
password = "Oi112466"
context = ssl.create_default_context()
mail = "meuraspinfo@gmail.com"

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