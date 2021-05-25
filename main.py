# TODO
# Multithreaded copying of files
# General cleanup

"""
        IMPORTS
"""
import eyed3
import os
import shutil
import time
import glob
from colorama import Fore, Back, Style
import queue
import threading

eyed3.log.setLevel("ERROR") # Gives a bunch of invalid date warnings otherwise

"""
        FUNCTIONS
"""
# Function that prints out a nice loading/procesing bar
def print_percent_complete(index, total, length, name, compress, width):
    percent_complete = round(((index+1)/total * 100), 1)
    
    complete = round(percent_complete/(100/length)) if not compress else round(percent_complete/(100/(width-2)))
    
    left = length - complete if not compress else width - 2 - complete
    complete_str = "█" * complete
    left_str = "░" * left
    buffer = " " * len("finished")

    if not compress:
        print(f"{buffer} {name}: [{Fore.GREEN}{complete_str}{Fore.YELLOW}{left_str}{Style.RESET_ALL}] {Fore.YELLOW}{percent_complete}% complete {Style.RESET_ALL}", end="\r")
    else:
        print(f"[{complete_str}{left_str}]", end="\r")
    if round(percent_complete) == 100:
        if not compress:
            print(f"Finished {name.lower()}: [{complete_str}{left_str}] {Fore.GREEN}{percent_complete}% complete {Style.RESET_ALL}")
        else:
            print("")

# Removes invalid characters from input string
def removeBadChars(s):
    bad = ["/", "\\", ":", "*", "?", "<", ">", "|"]
    _s = list(s)
    for char in range(len(_s)):
        if _s[char] in bad:
            _s[char] = "-"
    return "".join(_s)

# Assigns tasks to thread
q = queue.Queue()
def assign():
    while True:
        elem = q.get()
        if elem is None:
            break
        copy_worker(elem)
        q.task_done()

# Copy task for putting file in correct file structure
curCopy = 0
def copy_worker(elem):
    pass
    # TODO: transfer the code over to index based
    #   - Create missing directories
    #   - Copy the file over
    #   - Output
    #   - Clean up the actual code

    # for artist in outputStructure:
    #     pathToArtist = os.path.join("Output", removeBadChars(artist[0]))
    #     os.mkdir(pathToArtist)
    #     for album in artist[1]:
    #         pathToAlbum = os.path.join(pathToArtist, removeBadChars(album[0]))
    #         os.mkdir(pathToAlbum)
    #         for song in album[1]:
    #             shutil.copy(song[1], pathToAlbum)
    #             print_percent_complete(curCopy, totalSongs, barSize, "Copying", barSize <= 5, termSize[0])
    #             curCopy += 1

"""
        MAIN PROCESSING
"""

outputStructure = []
songsToSort = []
termSize = shutil.get_terminal_size()


# Finds all the songs that need to be organized
maxBar = termSize[0] - len("Finished scanning: [] 100.0! complete") - 1
barSize = min(maxBar, 75)

cur = 0
files = list(glob.iglob("Songs/**", recursive=True))
tot = len(files)
for file in files:
    print_percent_complete(cur, tot, barSize, "Scanning", barSize <= 5, termSize[0])
    cur += 1
    if os.path.isfile(file):
        songsToSort.append(file)

totalSongs = len(songsToSort)
print(f"{Fore.CYAN}Found {totalSongs} songs {Style.RESET_ALL}\n")


# Searches if it has a position and if it does place it otherwise create a directory for it
maxBar = termSize[0] - len("Finished sorting: [] 100.0! complete") - 1
barSize = min(maxBar, 75)

curSort = 0
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
    print_percent_complete(curSort, totalSongs, barSize, "Sorting", barSize <= 5, termSize[0])
    curSort+=1
print()


# Delete output folder if it already exists
try:
    shutil.rmtree("Output")
except:
    pass
os.mkdir("Output")


# Copy files to output folder
maxBar = termSize[0] - len("Finished copying: [] 100.0! complete") - 1
barSize = min(maxBar, 75)

threads = []
THREAD_NUM = 3

for i in range(THREAD_NUM):
    t = threading.Thread(target=assign)
    threads.append(t)
    t.start()

for artist_id in range(len(outputStructure)):
    for album_id in range(len(outputStructure[artist_id])):
        q.put((artist_id, album_id))
q.join()

for i in range(THREAD_NUM):
    q.put(None)

for t in threads:
    t.join()

print(f"\n{Fore.GREEN}Finished{Style.RESET_ALL}")