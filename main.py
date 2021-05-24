# TODO
# Implement SED for output - https://stackoverflow.com/questions/12714415/python-equivalent-to-sed
# Implement Colorama for coloured output
# Multithreaded processing of creating dirs for files
# Multithreaded copying of files
# General cleanup

import eyed3
import os
import shutil
import time
import glob
from colorama import Fore, Back, Style

eyed3.log.setLevel("ERROR") # Gives a bunch of invalid date warnings otherwise

def print_percent_complete(index, total, length, name, compress, width):
    percent_complete = round(((index+1)/total * 100), 1)
    
    complete = round(percent_complete/(100/length)) if not compress else round(percent_complete/(100/(width-2)))
    
    left = length - complete if not compress else width - 2 - complete
    complete_str = "█" * complete
    left_str = "░" * left
    buffer = " " * len("finished")

    if not compress:
        print(f"{buffer} {name}: [{complete_str}{left_str}] {Fore.YELLOW}{percent_complete}% complete {Style.RESET_ALL}", end="\r")
    else:
        print(f"[{complete_str}{left_str}]", end="\r")
    
    if round(percent_complete) == 100:
        if not compress:
            print(f"Finished {name.lower()}: [{complete_str}{left_str}] {Fore.GREEN}{percent_complete}% complete {Style.RESET_ALL}")
        else:
            print("")

outputStructure = []
songsToSort = []
termSize = shutil.get_terminal_size()
maxBar = termSize[0] - len("Finished scanning: [] 100.0! complete") - 1
print(maxBar)
barSize = min(maxBar, 75)

# Finds all the songs that need to be organized
cur = 0
files = list(glob.iglob("Songs/**", recursive=True))
tot = len(files)
for file in files:
    print_percent_complete(cur, tot, barSize, "Scanning", barSize <= 5, termSize[0])
    cur += 1
    time.sleep(0.02)
    if os.path.isfile(file):
        songsToSort.append(file)

print("Found " + str(len(songsToSort)) + " songs")
print("==================================================")
exit()
curSort = 1
# Searches if it has a position and if it does place it otherwise create a directory for it
for song in songsToSort:
    audiofile = eyed3.load(song)
    placed = 0 # 0 means found nothing, 1 means found artist, 2 means found album
    artistIndex = -1
    for artist in outputStructure:
        if audiofile.tag.artist == artist[0]:
            placed = 1
            artistIndex = outputStructure.index(artist)
            for album in artist[1]:
                if audiofile.tag.album == album[0]:
                    placed = 2
                    existing = False
                    for songCheck in album[1]:
                        if audiofile.tag.title == songCheck[0]:
                            existing = True
                    if not existing:
                        album[1].append([audiofile.tag.title, song])
    # Check if something was missing
    if placed != 2:
        if placed == 0:
            outputStructure.append([audiofile.tag.artist, [[audiofile.tag.album, [[audiofile.tag.title, song]]]]])
        elif placed == 1:
            outputStructure[artistIndex][1].append([audiofile.tag.album, [[audiofile.tag.title, song]]])
    print("Sorted song " + str(curSort) + " out of " + str(len(songsToSort)))
    curSort+=1
print("==================================================")

try:
    shutil.rmtree("Output")
except:
    pass
os.mkdir("Output")

def removeBadChars(s):
    bad = ["/", "\\", ":", "*", "?", "<", ">", "|"]
    _s = list(s)
    for char in range(len(_s)):
        if _s[char] in bad:
            _s[char] = "-"
    return "".join(_s)

curCopy = 1

for artist in outputStructure:
    pathToArtist = os.path.join("Output", removeBadChars(artist[0]))
    os.mkdir(pathToArtist)
    #print(artist[0])
    for album in artist[1]:
        pathToAlbum = os.path.join(pathToArtist, removeBadChars(album[0]))
        os.mkdir(pathToAlbum)
        #print("  ",album[0])
        for song in album[1]:
            shutil.copy(song[1], pathToAlbum)
            print("Copied song " + str(curCopy) + " out of " + str(len(songsToSort)))
            curCopy += 1
            #print("    ",song[0])