#! /usr/bin/python

import os
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree


bucket_list = []                                   # Need this empty list to start
deduped_buckets = []                               # Need this empty list to start
journal_fname = 'journal'                          # This should be whatever the current name of the journal files are
frozen_index_path = './foo_index/'                 # Don't forget the trailing slash
dest_index = './bar_index/'                        # Don't forget the trailing slash
search_string = 'source::WinEventLog:Security'     # The unique string to be used to find buckets


# Build a list of all the current buckets in the frozen index, this way we know the number of buckets to iterate over
def get_buckets():
    global bucket_list
    bucket_list = os.listdir(frozen_index_path + 'frozendb/')
    print('Starting frozen bucket count -> ' + str(len(bucket_list)))


# Find all occcurences of the string match, build new list of matching buckets, dedup the final list
def find_matches():
    matching_buckets = []
    count = 0
    for bucket in bucket_list:
        try:
            string_found = False
            count += 1
            journal_path = (frozen_index_path + 'frozendb/' + bucket + '/rawdata/' + journal_fname)
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


# Move all of the eligible buckets
def move_buckets():
    count = 0
    for bucket in deduped_buckets:
        count += 1
        src = (frozen_index_path + 'frozendb/' + bucket)
        dest = (dest_index + 'frozendb/' + bucket)
        print('Moving bucket ' + str(count) + ' of ' + str(len(deduped_buckets)) + ' from ' + src + ' to ' + dest + "\n")
        copy_tree(src, dest)
        remove_tree(src)


get_buckets()
print('Done Getting Buckets' + "\n")
find_matches()
print('Done Finding Matches' + "\n")
move_buckets()
print('Done Moving Buckets' + "\n")
