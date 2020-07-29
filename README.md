# Music folder management

## What does it do

I was busy expanding my Plex server library of songs and I have enough patience to manually add all of the ID3V2 tag information for any songs that don't have them but when it gets to organizing them into a nice directory structure it will just take too long. I decided to make this python program to do that for me. It takes the existing tag information for the artist, album and song title and reorganizes the music into a nice file system structure -> `Output/Artist/Album/Song.mp3`.

## Prerequisites

To use it make sure you have `eyed3` installed using `pip install eyeD3`. If you are on Windows make sure to install `python-magic-bin` using `pip install python-magic-bin`.

## How to use

To use the python script, put all of your songs into a folder called `Songs`. It does not matter if they are already partially sorted as it will go through the entire file tree. As long as they all have an ID3V2 tag for their title, album and artist it will organize it based on artist -> album -> song. Just run the python script and it should generate a directory called `Output`. It will copy across all of the songs into the sorted directories, so even if the program does fail you will still have your original files untouched. If they are not MP3 files modify the code on line 10 for any other extension. It is only tested with MP3's but it should work with any file that has ID3V2 tags.

### Tips for music organization in general

My tips/steps for organizing your music are pretty simple

1. Download your music from wherever you want
2. Add tag information if it is missing (I use Mp3tag on Windows and MusicBrainz Picard)
3. Normalize the volume (I use MP3Gain on Windows)
4. Run this script to organize it

MusicBrainz Picard is very powerful and if you have popular songs that are available everywhere it will be able to sort it and organize your entire library for you without having to use this script, but I have a lot of covers and other songs that I enjoy that are not in the library so that is where this alternative process comes in.
