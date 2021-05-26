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


"""
        MAJOR SETUP / GLOBAL VARIABLES
"""
eyed3.log.setLevel("ERROR") # Gives a bunch of invalid date warnings otherwise
threadLock = threading.Lock() # To be able to lock thread for counting purposes

TERM_SIZE = shutil.get_terminal_size() # Terminal size of loading bar output
MAX_BAR_SIZE = 75 # Maximum bar loding size
THREAD_NUM = 4 # Number of threads for output

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
def copy_worker(elem):
    global curCopy, maxBar, barSize

    # Deal with the artist
    pathToArtist = os.path.join("Output", removeBadChars(outputStructure[elem[0]][0]))
    with threadLock:
        if not os.path.exists(pathToArtist):
            os.mkdir(pathToArtist)

    # Deal with the album
    pathToAlbum = os.path.join(pathToArtist, removeBadChars(outputStructure[elem[0]][1][elem[1]][0]))
    with threadLock:
        if not os.path.exists(pathToAlbum):
            os.mkdir(pathToAlbum)

    # Copy the songs
    for song in outputStructure[elem[0]][1][elem[1]][1]:
        shutil.copy(song[1], pathToAlbum)
        print_percent_complete(curCopy, uniqueSongs, barSize, "Copying", barSize <= 5, TERM_SIZE[0])
        with threadLock:
            curCopy += 1

"""
        MAIN PROCESSING
"""

"""
    Output Structure = [[Artist1, [
                                    [AlbumA, [1, 2, 3]], 
                                    [AlbumB, [1, 2, 3]]]], 
                        [Artist2, [
                                    [AlbumC, [1, 2, 3]], 
                                    [AlbumD, [1, 2, 3]]]]]
"""
outputStructure = []
songsToSort = []


# Finds all the songs that need to be organized
maxBar = TERM_SIZE[0] - len("Finished scanning: [] 100.0! complete") - 1
barSize = min(maxBar, MAX_BAR_SIZE)

cur = 0
files = list(glob.iglob("Songs/**", recursive=True))
tot = len(files)
for file in files:
    print_percent_complete(cur, tot, barSize, "Scanning", barSize <= 5, TERM_SIZE[0])
    cur += 1
    if os.path.isfile(file):
        songsToSort.append(file)

totalSongs = len(songsToSort)
print(f"{Fore.CYAN}Found {totalSongs} songs {Style.RESET_ALL}\n")


# Searches if it has a position and if it does place it otherwise create a directory for it
maxBar = TERM_SIZE[0] - len("Finished sorting: [] 100.0! complete") - 1
barSize = min(maxBar, MAX_BAR_SIZE)

curSort = 0
uniqueSongs = 0
for song in songsToSort:
    audiofile = eyed3.load(song)
    placed = 0 # 0 means found nothing, 1 means found artist, 2 means found album
    artistIndex = -1
    existing = False
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
    print_percent_complete(curSort, totalSongs, barSize, "Sorting", barSize <= 5, TERM_SIZE[0])
    curSort += 1
    if not existing:
        uniqueSongs += 1
print(f"{Fore.CYAN}Sorted {uniqueSongs} unique songs {Style.RESET_ALL}\n")


# Delete output folder if it already exists
try:
    shutil.rmtree("Output")
except:
    pass
os.mkdir("Output")

# Copy files to output folder
curCopy = 0
maxBar = TERM_SIZE[0] - len("Finished copying: [] 100.0! complete") - 1
barSize = min(maxBar, MAX_BAR_SIZE)

threads = []

for i in range(THREAD_NUM):
    t = threading.Thread(target=assign)
    threads.append(t)
    t.start()

for artist_id in range(len(outputStructure)):
    for album_id in range(len(outputStructure[artist_id][1])):
        q.put((artist_id, album_id))
q.join()

for i in range(THREAD_NUM):
    q.put(None)

for t in threads:
    t.join()
print(f"{Fore.CYAN}Copied {uniqueSongs} songs{Style.RESET_ALL}")

print(f"\n{Fore.GREEN}Finished{Style.RESET_ALL}")