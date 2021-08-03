#! /usr/bin/python

""" Splunk frozen bucket find and move script

A simple script to search through a given index (directory) where frozen data
has been written that actually needs to be in separate indexes. This solution
arises from a scenario where a splunk environment was improperly configured.
That misconfiguration resulted in multiple indexes freezing buckets into a
single directory. The assumption is that if you can find a string of text within
the journal files, that is unique to events belonging to a single index, you can
use this script to search all the journals, find all buckets that match, compile
that list of directories, and then finally move them into the correct
destination index.

Requires two libraries, os and distutils

Main consists of three primary functions calls...

get_buckets  - Builds a list of all buckets in the index. Gives us a finite list 
               to iterate over for searching.
find_matches - Finds the first occurence of search_string as it iterates over
               all buckets in bucket_list. This yields a list of buckets to be
               moved.
move_buckets - Copies found buckets into the destination directory. If
               succesful, remove the source from the old path.
"""

import os
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree


bucket_list = []                               # Need this empty list to start
deduped_buckets = []                           # Need this empty list to start
journal_fname = 'journal'                      # The name of your journal files
source_index = './foo_index/'                  # Don't forget the trailing slash
dest_index = './bar_index/'                    # Don't forget the trailing slash
search_string = 'source::WinEventLog:Security' # Your unique search string


def get_buckets():
    """Builds a list of all buckets in the index.

    Parameters
    ----------
    None

    Returns
    -------
    bucket_list
        A list of all of the buckets in the index (directory)
    """

    global bucket_list
    bucket_list = os.listdir(source_index + 'frozendb/')
    print('Starting frozen bucket count -> ' + str(len(bucket_list)))


def find_matches():
    """Finds all the buckets that have a matching string

    Parameters
    ----------
    None

    Returns
    -------
    deduped_buckets
        A list of buckets containing files with matches to search_string
    """

    count = 0
    matching_buckets = []
    for bucket in bucket_list:
        try:
            count += 1
            string_found = False
            journal_path = (source_index + 'frozendb/' + bucket + '/rawdata/' + journal_fname)
            print('Current matching bucket count is -> ' + str(len(matching_buckets)))
            print('Reading bucket ' + str(count) + ' of ' + str(len(bucket_list)) + ' in file ' + journal_path)
            with open(journal_path, 'r') as input_file:
                line_number = 0
                for line in input_file:
                    if string_found is False and search_string in line:
                        line_number += 1
                        string_found = True
                        matching_buckets.append(bucket)
                    elif string_found is True:
                        print('Matching string found on line -> ' + str(line_number))
                        break
            print('')
        except:
            print('Issue with bucket -> ' + bucket + "\n")
            continue
    global deduped_buckets
    deduped_buckets = list(dict.fromkeys(matching_buckets))
    print('Buckets found with matching string -> ' + str(len(deduped_buckets)) + "\n")


def move_buckets():
    """Copies and removes source buckets if copy is successful

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    count = 0
    for bucket in deduped_buckets:
        count += 1
        src = (source_index + 'frozendb/' + bucket)
        dest = (dest_index + 'frozendb/' + bucket)
        print('Moving bucket ' + str(count) + ' of ' + str(len(deduped_buckets)) + ' from ' + src + ' to ' + dest + "\n")
        copy_tree(src, dest)
        remove_tree(src)

def main():
    get_buckets()
    print('Done Getting Buckets' + "\n")
    find_matches()
    print('Done Finding Matches' + "\n")
    move_buckets()
    print('Done Moving Buckets' + "\n")

if __name__ == "__main__":
    main()