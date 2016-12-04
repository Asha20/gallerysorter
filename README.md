# gallerysorter


## What does this program do?

My phone's camera, when creating files, uses a specific format to construct a name for the file. The purpose of *gallerysorter* is to automatically sort these files into appropriate subfolders.

I had a folder with photos taken with my phone's camera that looked something like this:

    photos
    ├── 20160113_072355.jpg
    ├── 20160202_175535.mp4
    ├── 20160205_051739.jpg
    ├── 20160210_112559.mp4
    ├── 20160226_042816.jpg
    └── 20160324_125037.mp4
	
A common trend among these photos is that their name represents the date they've been taken. Take a look at the example, `20160113_072355.jpg`:

File | Year | Month | Day | Hour | Minute | Second
---- | ---- | ----- | --- | ---- | ------ | ------
20160113_072355.jpg | 2016 | 01 | 13 | 07 | 23 | 55

For a file to fulfill this format, it has to have the following properties:

* First 4 characters represent the year.
* 5-6 represent the month.
* 7-8 represent the day.
* 9 is an underscore.
* 10-11 represent the hour.
* 12-13 represent the minute.
* 14-15 represent the second.
* Extension goes after these 15 characters.

Files that match these characteristics will from here be referred to as **timefiles**.

*gallerysorter* uses this data to organize timefiles like this:

    photos
    └── 2016
        ├── February 2016
        │   ├── 20160202_175535.mp4
        │   ├── 20160205_051739.jpg
        │   ├── 20160210_112559.mp4
        │   └── 20160226_042816.jpg
        ├── January 2016
        │   └── 20160113_072355.jpg
        └── March 2016
    	    └── 20160324_125037.mp4


## Installation guide

1. Clone the repository
2. Enter the directory using `cd gallerysorter`
3. Run the program: `python3 gallerysorter.py`


## Tests

Tests can be run from the base directory of the repository.
Use `python3 -m unittest discover`


## How to use

*gallerysorter* has 2 commands: **sort** and **list**.


### list

    usage: gallerysorter.py list [-h] [-r] [-e EXTENSIONS [EXTENSIONS ...]] source
    
The **list** command will print out all of the timefiles that have an allowed extension.

Argument | Use
-------- | ---
source | The directory containing the timefiles you want to list.
-r | Lists the *source*'s timefiles **recursively**.
-e | Filter the **extensions** the program will search for (Default: JPG and MP4.)

### sort

    usage: gallerysorter.py sort [-h] [-r] [-c] [-v] [-e EXTENSIONS [EXTENSIONS ...]] source [destination]
    
The **sort** command is used to sort timefiles within a directory.

Argument | Use
-------- | ---
source | The directory containing the timefiles you want to organize.
destination | The base directory to organize the files in (Default: same as *source*.)
-r | Sorts the timefiles in the *source* **recursively**.
-c | **Copies** files into *directory* instead of moving them.
-v | Prints out the timefiles as they're being organized in a **verbose** manner.
-e | Filter the **extensions** the program will sort (Default: JPG and MP4.)


## License

See `LICENSE.md`

