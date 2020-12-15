import eyed3, os, shutil
eyed3.log.setLevel("ERROR") # Gives a bunch of invalid date warnings otherwise

ARTIST=""
ALBUM=""

# Sets the metadata for songs based on filename
for root, dirs, files in os.walk("Songs"):
    for file in files:
        if file.endswith(".mp3"):
            audiofile = eyed3.load(file)
            audiofile.tag.artist=ARTIST
            audiofile.tag.album=ALBUM
            audiofile.tag.title=file[:-4]
            audiofile.tag.save()
            print("Set metadata for " + file)