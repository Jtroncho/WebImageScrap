import argparse
import urllib.request
import sys
import os
import time as t

from os import listdir
from os.path import isfile, join

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def parseArguments():
	parser = argparse.ArgumentParser(
		description="Get all the Images of a webpage.")
	parser.add_argument(
		"website", help="Websites separated by commas to extract images from, like: https://www.python.org/ or https://www.python.org/,https://docs.python.org/3/")
	parser.add_argument(
		"-s", "--start", help="Website to Start from", default=None)
	# parser.add_argument("-il","--imgLink", help="Where are the images from..., like: website=https://www.python.org/ imgLink=https://www.python.org/images/", default=None)
	# parser.add_argument("-d", "--dont", help="", default=None)
	parser.add_argument(
		"-o", "--output", help="Path to store images.", default="imgs")

	global args
	args = parser.parse_args()

	if args.start == None:
		args.start = args.website

	print(args.website)
	print(args.start)
	print(args.output)


def checkOrCreateDir():
	try:
		os.stat(args.output)
		global downloadedImgs
		downloadedImgs = [f for f in listdir(
			args.output) if isfile(join(args.output, f))]
		print("Imagenes ya descargadas: {}".format(len(downloadedImgs)))
	except:
		os.mkdir(args.output)


def getHrefs(webDriver, toVisit, visited):
	aElements = webDriver.find_elements_by_tag_name('a')
	# print ("a Elements: {}".format(len(aElements)))
	pagesURL = []
	for aElement in aElements:
		linkReference = aElement.get_attribute('href')
		# print(args.start)
		if linkReference != None and not (".pdf" in linkReference) and not ("#" in linkReference):
			# print(linkReference)
			if args.website in linkReference:
				pagesURL.append(linkReference)
			elif "/" in linkReference[0]:
				pagesURL.append(args.website + linkReference)
	newPages = list(set(pagesURL) - set(visited + toVisit))
	# print ("URLs Encontradas: {}".format(pagesURL))
	print("URLs nuevas: {}".format(len(newPages)))
	print("URLs visitadas: {}".format(len(visited)))
	# print ("URLs por visitar: {}".format(len(toVisit)))
	return newPages


def getImgs(webDriver, imgExt):
	html = webDriver.find_elements_by_tag_name('img')
	names, sources = [], []
	for image in html:
		src = image.get_attribute('src')
		imgName = src.split("/")[-1]
		# print("Image Name: ", imgName)
		if "." in imgName:
			imageExtension = imgName[imgName.rfind("."):imgName.rfind(".")+4]
			if imageExtension in imgExt:
				imgName = imgName[:imgName.rfind(".")+4]
				sources.append(src)
				names.append(imgName)
	return names, sources

# ----------------------------------------------MAIN


parseArguments()
checkOrCreateDir()

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
extensions = [".jpg", ".jpeg", ".png"]

try:
	filePath = args.output
	if args.output[-1] != "/":
		filePath += "/"
	# driver.get(args.website)
	print("Driver Iniciado")
	# t.sleep(5)
	visitedWebs = []  # ["http://www.fillogy.com/en/logout.html", "http://www.fillogy.com/de/abmelden.html"] #webs que no quieres que se visiten
	visitWebs = [args.start]

	while len(visitWebs) > 0:
		# print ("Por visitar: {}".format(len(visitWebs)))
		print("URLs por visitar: {}".format(len(visitWebs)))
		visit = visitWebs.pop()

		visitedWebs.append(visit)
		print("Visitando: {}".format(visit))
		try:
			driver.get(visit)

			imagesName, imagesSource = getImgs(driver, extensions)
			for i in range(len(imagesSource)):
				if imagesName[i] != None:
					if imagesName[i] not in downloadedImgs:
						print("Archivo: {}".format(imagesName[i]))
						downloadedImgs.append(imagesName[i])
						try:
							urllib.request.urlretrieve(imagesSource[i], filePath + imagesName[i])
						except:
							print("Unexpected error 1: {}".format(sys.exc_info()))  # [0]))
					else:
						print("Imagen ya descargada: {}".format(imagesName[i]))
			print()

		except:
			print("Unexpected error 2: {}".format(sys.exc_info()))  # [0]))
			print()

		finally:
			visitWebs.extend(getHrefs(driver, visitWebs, visitedWebs))

except:
	print("Unexpected error 3: {}".format(sys.exc_info()))  # [0]))

finally:
	driver.close()
