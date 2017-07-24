My personal scrips for the raw developer: [Darktable](https://www.darktable.org/ "darktable homepage")

# Script list
## purge_non_existing_images
Have two version, a slightly modified version for compatibility and the faster python version

|Source|Images|SQL Instructions|Execution time|
|------|------|----------------|----|
python script|6704|2206 (as 1 transaction)|<1 second
modified shell script|6704|2206 (as 1 transaction)|17 second
original shell script|6704|2206|176 second


### Python
A python port for the `purge_non_existing_images.sh` script. Its faster finding the images to be removed and delete all references as a transaction.
### Shell
Added transactions for faster processing.

