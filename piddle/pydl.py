#!/usr/bin/env python2
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Filename: pydl.py                                                 #
# Authors: Brian Tomlinson <darthlukan@gmail.com>                   #
#          Manuel Debaux <debaux.manual@gmail.com>                  #
#          Brian Turner <archkaine@gmail.com>                       #
# URL: git@github.com:darthlukan/piddle.git                         #
# Description: A simple CLI download manager written in Python.     #
# Warning: If you received this program from any source other than  #
# the above noted URL, please check the source code! You may have   #
# downloaded a file with malicious code injected.                   #
# License: GPLv2, Please see the included LICENSE file.             #
# Note: This software should be considered experimental!            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import os
import urllib2
import argparse
import fileinput
from progressbar import *
from threading import Thread # Because multi-threading is bad a$$! :)

# Now we are going to define the actual program API, these are the functions
# that are going to actually do work.  TODO: A class should go in here somwhere
# to keep things clean and to properly use multi-threading.

def query_response(question):
    prompt = " [y/n/q] "
    response = raw_input(question + prompt).lower()
    if response == 'q':
        clean_exit()
    elif response == 'y' or response == 'n':
        return response;
    else:
        print('Invalid response recorded, please try again.\n')
        query_response(question)


# The function that actually gets stuff
def get_reg_download(urlToGetFile, fileNameToSave):  # Grab the file(s)
    filelen=0
    data=str(urllib2.urlopen(urlToGetFile).info())
    data=data[data.find("Content-Length"):]
    data=data[16:data.find("\r")]
    filelen+=int(data)

    # Placeholder for progressbar:
    widgets = ['Download Progress: ', Percentage(), ' ',
                   Bar(marker='>', left='[',right=']'),
                   ' ', ETA(), ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=filelen).start()
    urllib2.urlopen(urlToGetFile, fileNameToSave)
    for i in range(filelen):
        pbar.update(i+1)
    pbar.finish()
    more_to_do_query()

# This looks redundant now, but just wait... :)
def get_special_download(urlToGetFile, baseDir):
    urllib2.urlopen(urlToGetFile, baseDir)

# This gets the overall length of the download job, used in progressbar
def get_overall_length(fileNameUrls, baseDir):
    fi = fileinput.input(fileNameUrls)
    overallLength = 0
    for line in fi:
        data = str(urllib2.urlopen(line).info())
        data = data[data.find('Content-Length'):]
        data = data[16:data.find('\r')]
        overallLength += int(data)
    special_download_work(fileNameUrls, baseDir, overallLength)

# Oh, you thought you were done? Nope, I'm gonna ask you more questions :)
def more_to_do_query():
    moreDownloads = query_response('Do you want to download more files?(y/n): ')
    if moreDownloads == 'n':
        print('Until next time!')
        clean_exit()
    elif moreDownloads == 'y':
            print('Re-routing...')
            ig.file_loop_check()
    else:
        print('Something bad happened, please report this error to the creator.')
        clean_exit()

# Do some work and give us a progressbar
def special_download_work(fileNameUrls, baseDir, overallLength):
    if not baseDir.endswith('/') and baseDir != '':
        baseDir += '/'
    fi = fileinput.input(fileNameUrls)
    nl = 0
    for line in fi:
        nl += 1
    fi = fileinput.input(fileNameUrls)
    cl = 0
    widgets = ['Overall Progress: ', Percentage(), ' ',
                Bar(marker = '>', left = '[', right = ']'),
                ' ', ETA(), ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets = widgets, maxval = overallLength)
    pbar.start()
    for line in fi:
        urlToGetFile = line[:-1]
        fileNameToSave = os.path.join(baseDir,urlToGetFile[urlToGetFile.rfind('/')+1:])
        get_special_download(urlToGetFile, fileNameToSave)
        cl += 1
        pbar.update(overallLength / nl * cl)
        for i in xrange(overallLength):
            pbar.update(i+1)
    pbar.finish()
    print('All done!')
    more_to_do_query()

class InfoGather:
    #This function is going to handle our special download info for file looping.
    def special_download_info(self):
        fileNameUrls = raw_input('Enter the filename (with path) that contains URLs (Q to quit): ')
        if fileNameUrls.upper() == 'Q':
            clean_exit()
        baseDir = raw_input('Enter the directory path where you want the files saved (Q to quit): ')
        if baseDir.upper() == 'Q':
            clean_exit()
        get_overall_length(fileNameUrls, baseDir)

    # Regular download setup
    def reg_download_info(self):
        urlToGetFile = raw_input('Please enter the download URL (Q to quit): ')
        if urlToGetFile.upper() == 'Q':
            clean_exit()
        fileNameToSave = raw_input('Enter the desired path and filename (Q to quit): ')
        if fileNameToSave.upper() == 'Q':
            clean_exit()
        get_reg_download(urlToGetFile, fileNameToSave)

    # Initial tests to decide where to go
    def file_loop_check(self):
        specialDownload = query_response('Do you need to import a file with links?')
        if specialDownload == 'n':
            self.reg_download_info()
        else:
            self.special_download_info()

# This is the function that starts it all
def main():
    print("Hello! I am going to ensure that downloading your files, renaming them, ")
    print("and specifying where to save them, are as simple as possible. Let's get to it!")
    
    # Argument parsing, wheeee!!!
    parser = argparse.ArgumentParser(description='pydl argument information.')
    parser.add_argument('-f', '--file', nargs='*',  action='append', dest='cFiles',
           help='Given the full path load each URL in the file. This will also take multiple file arguments.')
    parser.add_argument('-d', '--dir',   nargs=1, action= 'store', default=".", dest='outputDir',
           help='In a given directory check all files for URLs and download those.')
    parser.add_argument('-u', '--url', nargs='*', action='append', dest='cUrls',
           help='This will grab 1-N urls. Use space as the delimitter.')
    parser.add_argument('-o', '--output', nargs=1,  action='store', dest='outputDir',
           help='Move all downloaded files to this directory.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s-0.1dev',
           help ='Current version of pydl.py')

    # Lets define an instance of our info class here
    ig = InfoGather()

    # Do stuff
    args = parser.parse_args()
    if(args.cFiles):
        for file in args.cFiles:
            tx = Thread(target=getOverallLength(file,args.outputDir[0]))
            print("thread start")
            tx.start()
        #get_overall_length(file,args.outputDir[0])
    elif(args.cUrls):
            for url in args.cUrls:
                print("this hasn't been configured yet.")
    else:
        ig.file_loop_check()

#A function to provide a clean exit from anywhere in the program
def clean_exit():
        print ("Thank you for using piddle.")
        exit(0)

# Call main function
if __name__ == '__main__':
    main()