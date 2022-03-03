
import sys
import pathlib
import streamdb

#General ToDo:
#
# Error handling
#
#
#



def main():
    if sys.argv[0] == 'updatedb':
        streamdb.updatedb([])
    if sys.argv[0] == 'help':
        pass
        #ToDo, print help text
    else:
        print('Invalid args, try help')

if __name__ == '__main__':
    main()