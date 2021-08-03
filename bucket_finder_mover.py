#! /usr/bin/python

"""Splunk frozen bucket find and move script


A simple script to search through a given index (directory) where frozen data
has been written that actually needs to be in separate indexes. This solution
arises from a scenario where a splunk environment was improperly configured.
That misconfiguration resulted in multiple indexes freezing buckets into a
single directory. The assumption is that if you can find a string of text within
the journal files, that is unique to events belonging to a single index, you can
use this script to search all the journals, find all buckets that match, compile
that list of directories, and then finally move them into the correct
destination index.

Requires no third party libraries

Main function consists of three primary functions calls:
  get_buckets  - Builds a list of all buckets in the index. Gives us a finite list to iterate over for searching.
  find_matches - Finds the first occurence of search_string as it iterates over all buckets in bucket_list. This yields a list of buckets to be moved.
  move_buckets - Copies found buckets into the destination directory. If succesful, remove the source from the old path.
"""

import os
import argparse
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree


bucket_list = []                               # Need this empty list to start
deduped_buckets = []                           # Need this empty list to start
journal_fname = 'journal'                      # The name of your journal files


def get_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'src_idx',
        type = str,
        help = "The absolute or relative path to the source frozen index"
    )
    parser.add_argument(
        'dest_idx',
        type = str,
        help = "The absolute or relative path to the destination frozen index"
    )
    parser.add_argument(
        'search_string',
        type = str,
        help = "The text chars you want to search for in all journal files"
    )
    args = parser.parse_args()
    get_args.src_idx = args.src_idx
    get_args.dest_idx = args.dest_idx
    get_args.search_string = args.search_string 


def get_buckets():
    get_buckets.bucket_list = os.listdir(get_args.src_idx + 'frozendb/')
    print('Starting frozen bucket count -> ' + str(len(get_buckets.bucket_list)))


def find_matches():
    count = 0
    matching_buckets = []
    for bucket in get_buckets.bucket_list:
        try:
            count += 1
            string_found = False
            journal_path = (get_args.src_idx + 'frozendb/' + bucket + '/rawdata/' + journal_fname)
            print('Current matching bucket count is -> ' + str(len(matching_buckets)))
            print('Reading bucket ' + str(count) + ' of ' + str(len(get_buckets.bucket_list)) + ' in file ' + journal_path)
            with open(journal_path, 'r') as input_file:
                line_number = 0
                for line in input_file:
                    if string_found is False and get_args.search_string in line:
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
    find_matches.deduped_buckets = list(dict.fromkeys(matching_buckets))
    print('Buckets found with matching string -> ' + str(len(find_matches.deduped_buckets)) + "\n")


def move_buckets():
    count = 0
    for bucket in find_matches.deduped_buckets:
        count += 1
        src = (get_args.src_idx + 'frozendb/' + bucket)
        dest = (get_args.dest_idx + 'frozendb/' + bucket)
        print('Moving bucket ' + str(count) + ' of ' + str(len(find_matches.deduped_buckets)) + ' from ' + src + ' to ' + dest + "\n")
        copy_tree(src, dest)
        remove_tree(src)

def main():
    get_args()
    get_buckets()
    print('Done Getting Buckets' + "\n")
    find_matches()
    print('Done Finding Matches' + "\n")
    move_buckets()
    print('Done Moving Buckets' + "\n")

if __name__ == "__main__":
    main()