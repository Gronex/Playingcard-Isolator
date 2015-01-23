#!/usr/bin/python2

import cv2
import sys, getopt, argparse
import numpy as np
import ImageHandler as ih
import re
import glob, os, errno

def is_dir(dirname):
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return os.path.normpath(dirname)

def handleArgs():
    #TODO: Override files argument
    #TODO: maybe add multi card file support?

    outfolderName = "output"
    images = []
    outfolder = None
    outPath = None

    parser = argparse.ArgumentParser(description="Takes pictures of cards and cuts, turns and resizes them to fit normal card size.")

    #The different types of arguments available
    parser.add_argument("-i", "--infile", nargs="+", type=argparse.FileType('r'), help="the imagefile(s) to process.")
    parser.add_argument("-d", "--dir", nargs="+", type=is_dir, help="the directories to look for files in.")
    parser.add_argument("-o", "--outfolder", type=is_dir, help="the dir to save the pictures in. If not indicated pictures will not be saved.")
    parser.add_argument("-c", "--createfolder", help="indicates that a folder for the output files should be created either in root path, or after outfolder in '{0}'".format(outfolderName), action="store_true")
    parser.add_argument("--nowindow", help="removes the windows result window", action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--version", action="version", version="%(prog)s -- version 1.1")


    args = parser.parse_args()

    #Force use of infile or dir
    if not (args.infile or args.dir):
        print("You need to use -i/--infile or -d/--dir to indicate which file(s) to work on")
        return [], None

    #Handle arguments
    if args.infile:
        for imgFile in args.infile:
            images.append(imgFile.name)

    if args.dir:
        #Supported image formats by opencv
        fileTypes = ('*.png', '*.jpg', '*.jpeg', '*.jpe', '*.jp2', '*.bmp', '*.pbm', '*.pgm', '*.ppm', '*.sr', '*.ras', '*.tiff', '*.tif')
        if args.verbose:
            print("Looking for files in {}".format(args.dir))
        for arg in args.dir:
            for fileType in fileTypes:
                images.extend(glob.glob("{0}/{1}".format(arg, fileType)))

    if args.outfolder:
        if args.createfolder:
            outPath = "{0}/{1}".format(args.outfolder, outfolderName)
        else:
            outPath = "{0}".format(args.outfolder)
        if args.verbose:
            print("Output will be saved in: {0}".format(os.path.abspath(outPath)))
        createFolder(outPath, args.verbose)
    return images, outPath, args

def createFolder(path, verbose=False):
    try:
        os.makedirs(path)
        if verbose:
            print("Directory '{0}' created".format(path))
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise

def getFilename(fileName, number=-1):
    fileName = os.path.splitext(fileName)
    fileName = os.path.basename(fileName[0])
    if number > 0:
        fileName = "{0}{1:02d}".format(fileName, number)
    return fileName



#Main controller area
if __name__ == "__main__":
    dimentions = (214, 300)

    images, outPath, args = handleArgs()
    verbose = args.verbose
    nowindow = args.nowindow
    if len(images) > 0:
        print("Files to process: {}".format(images))
    else:
        print("No files to process")
        sys.exit()

    for fileName in images:

        image = cv2.imread(fileName)
        if image == None:
            print("Can't find '{}'".format(fileName))
            continue
        if verbose:
            print("Working of file: {0}".format(fileName))
        imgray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        if verbose:
            print("Finding contours...")
        boxes = ih.findMultipleRects(imgray, verbose)

        if len(boxes) < 1:
            print("No contours found")
            continue

        for i in range(len(boxes)):
            result = image.copy()
            #TODO:Correct for nonupright cards
            transform, finaldimentions = ih.transformImage(boxes[i], dimentions)
            if transform == None:
                continue

            #Append numbers if multicard pucture
            if len(boxes) > 1:
                finalName = getFilename(fileName, i+1)
            else:
                 finalName = getFilename(fileName, -1)
            result = cv2.warpPerspective(result, transform, finaldimentions)
            if result != None:
                #TODO: ajustable file type, and name
                #TODO: Don't override
                if outPath != None:
                    cv2.imwrite("{0}/{1}.jpg".format(outPath, finalName), result)
                if not nowindow:
                    cv2.imshow("Result: {0}".format(finalName), result)
            else:
                print("No result for {}".format(fileName))
    #Close all windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()
