# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import requests
import argparse
from bs4 import BeautifulSoup

from urllib.parse import urlparse
import sys
import os
import time as t
from os import listdir
from os.path import isfile, join

def parseArguments():
    parser = argparse.ArgumentParser(
        description="Get all the Images from website.")
    parser.add_argument("-w", "--websites", help="Websites scrap images from", default="./websites.txt")
    parser.add_argument(
        "-d", "--depth", help="Times to recursively explore the linked webpages for image scraping", default=1, type=int)
    parser.add_argument(
        "-dm", "--domain", help="Limit to webpages on the same domain", action="store_true")
    parser.add_argument("-e", "--extensions", help="Image type file")
    parser.add_argument("-dp", "--duplicate",
                        help="Save images with same name", action="store_true")
    parser.add_argument(
        "-o", "--output", help="Path to store images", default="images")
    parser.add_argument(
        "-v", "--verbose", help="Increase output verbosity", action="store_true")
    
    global args
    args = parser.parse_args()
    print(args)
    print(args.websites)
    print(args.output)

def parseWebsitesFile():
    global websites
    try:
        my_file = open(args.websites, "r")
        data = my_file.read()
        websites = data.split("\n")
        print(websites)
        print()
    except:
        print("Unexpected error 2: {}".format(sys.exc_info()))
    finally:
        my_file.close()

def checkAlreadyDownloadedImages():
    global downloadedImages
    downloadedImages = [f for f in listdir(
        args.output) if isfile(join(args.output, f))]
    print("Already downloaded images: {}".format(len(downloadedImages)))

def createDir():
    try:
        os.stat(args.output)
    except:
        os.mkdir(args.output)
    if args.output[-1] != "/":
        args.output += "/"

def getDomain(website):
    return urlparse(website).netloc

def scrapHrefs(page):
    hrefs = []
    for link in page.find_all('a'):
        hrefs.append(link.get('href'))
    hrefs = list(set(hrefs))
    return hrefs

def scrapImgs(page):
    imgs = []
    for link in page.find_all('img'):
        imgs.append(link.get('src'))
    imgs = list(set(imgs))
    return imgs

def saveImage(imageLink):
    response = requests.get(imageLink)
    with open(args.output + os.path.basename(urlparse(imageLink).path), 'wb') as file:
        file.write(response.content)

def saveVisitedWebsites(websites):
    saveLineOnFile("Visited Websites:")
    with open(args.output + "visited.txt", 'a') as file:
        file.write(str("\n"))
        file.write("".join(str(item) for item in websites))

def saveLineOnFile(text):
    with open(args.output + "visited.txt", 'a') as file:
        file.write(str("\n"))
        file.write(str(text))

def downloadImages(images):
    saveLineOnFile("Images:")
    for link in images:
        saveImage(link)
        saveLineOnFile(link)

def getImgsAndHrefs(website):
    print("website: ", website)
    saveLineOnFile("Website:")
    saveLineOnFile(website)
    domain = "http://" + getDomain(website)

    page = BeautifulSoup(requests.get(website).content, 'html.parser')

    imgs = scrapImgs(page)
    imgs = [x for x in imgs if (os.path.basename(urlparse(x).path) not in downloadedImages)]
    hrefs = scrapHrefs(page)
    for x in hrefs:
        if(x == None or len(x)<2):
            hrefs.remove(x)
        elif (args.domain and x[0] != "/"):
            hrefs.remove(x)
    hrefs = [domain+x for x in hrefs]


    print("Images found", len(imgs),"|","Links found", len(hrefs))
    
    return imgs, hrefs

def getDataInDepth(depthWebsites):
    websitesToVisit = []
    for website in depthWebsites:
        imgs, hrefs = getImgsAndHrefs(website)
        if (args.verbose):
            print("imgs ", imgs)
            print("hrefs ", hrefs)
        downloadImages(imgs)
        newHrefs = [x for x in hrefs if x not in websitesToVisit]
        websitesToVisit.extend(newHrefs)
    return websitesToVisit

def main():
    parseArguments()
    createDir()
    checkAlreadyDownloadedImages()
    parseWebsitesFile()

    depth = []
    depth.append(websites)

    for depthIteration, depthWebsites in enumerate(depth, start=1):
        if (args.verbose):
            print("Actual depth: ", depthIteration, "|| depth: ", depth)
        depth.append(getDataInDepth(depthWebsites))
        saveVisitedWebsites(depthWebsites)
        if (depthIteration >= args.depth):
            break

if __name__ == "__main__":
    main()