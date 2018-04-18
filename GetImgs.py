import argparse
import urllib.request
import sys, os, time as t

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

parser = argparse.ArgumentParser(description="Get all the Images of a webpage.")
parser.add_argument("website", help="Websites separated by commas to extract images from, like: https://www.python.org/ or https://www.python.org/,https://docs.python.org/3/")
parser.add_argument("-o", "--output", help="Path to store images.", default="imgs")
args = parser.parse_args()

if args.output:
	try:
		os.stat(args.output)
	except:
		os.mkdir(args.output)

try:
	#options for a Headless Firefox
	#options = Options()
	#options.add_argument("--headless")
	#driver = webdriver.Firefox(firefox_options=options, executable_path="")
	#print("Firefox Headless Browser Invoked")

	driver = webdriver.Firefox()
	t.sleep(5)

	webs = args.website.split(",")
	for websiteURL in webs:
		driver.get(websiteURL)
		imagesHTML = driver.find_elements_by_tag_name('img')
		for image in imagesHTML:
			src = image.get_attribute('src')
			filePath = args.output 
			if args.output[-1] != "/":
				filePath += "/"
			filePath += src.split("/")[-1]
			urllib.request.urlretrieve(src, filePath)

except:
	print ("Unexpected error: {}".format(sys.exc_info()[0]))

finally:
	driver.close()