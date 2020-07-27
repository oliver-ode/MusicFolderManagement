import eyed3, os, shutil
eyed3.log.setLevel("ERROR") # Gives a bunch of invalid date warnings otherwise

outputStructure = []
songsToSort = []

# Finds all the songs that need to be organized
for root, dirs, files in os.walk("Songs"):
    for file in files:
        if file.endswith(".mp3"):
            songsToSort.append(os.path.join(root, file))

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