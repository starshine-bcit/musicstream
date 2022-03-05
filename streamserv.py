
import sys
import pathlib
import streamdb

DBLOC = pathlib.Path('streamserv.db')

# General ToDo:
#
# 
#
#
#


def main():
    if sys.argv[1] == 'db':
        if sys.argv[2] == 'create':
            userpath = pathlib.Path(sys.argv[3])
            if userpath.exists() and userpath.is_absolute():
                if not DBLOC.is_file():
                    streamdb.createdb(userpath)
                else:
                    streamdb.recreatedb(userpath)
            else:
                print('Error: Invalid or relative path supplied')
        elif sys.argv[2] == 'stats':
            if pathlib.Path.is_file(DBLOC):
                streamdb.statsdb()
            else:
                print(f'Error: You cannot have database stats without a {DBLOC}')
    elif sys.argv[1] == 'help':
        pass
        # ToDo, print help text
    else:
        print('Invalid args, try help')

if __name__ == '__main__':
    main()
