
import pathlib
import sqlite3
import eyed3
import datetime

DBLOC = pathlib.Path('streamserv.db')


def opendb():
    con = sqlite3.connect(DBLOC)
    cur = con.cursor()
    return con, cur


def createdb(scanpath):
    # scans given directory for mp3 files and loads them into a simple database
    try:
        # create database info table
        con, cur = opendb()
        cur.execute('''CREATE TABLE songs (
                        id integer PRIMARY KEY,
                        path text NOT NULL,
                        filename text NOT NULL,
                        length integer NOT NULL,
                        mtime int NOT NULL,
                        title text,
                        artist text,
                        album text
                        ); ''')

        print(f'Creating database...'
              f'\n{DBLOC} in current directory'
              f'\nLibrary location: {str(scanpath)}')

        tid = 0
        for file in scanpath.rglob('*.mp3'):
            # set null values in the event tags are missing
            id3 = eyed3.load(pathlib.PurePath(file))
            ttitle = 'NULL'
            tartist = 'NULL'
            talbum = 'NULL'
            ttitle = id3.tag.title
            tartist = id3.tag.artist
            talbum = id3.tag.album

            insertstate = '''INSERT INTO songs (id, 
                            path,
                            filename,
                            length,
                            mtime,
                            title,
                            artist,
                            album)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);'''

            insertvals = (tid,
                          str(file),
                          file.name,
                          int(id3.info.time_secs),
                          int(file.stat().st_mtime),
                          ttitle,
                          tartist,
                          talbum)

            cur.execute(insertstate, insertvals)
            tid += 1
    except sqlite3.Error as error:
        print('DB Error:', error)
    else:
        print(f'\nDatabase creation success')
    finally:
        con.commit()
        con.close()


def recreatedb(scanpath):
    print(f'Warning: {DBLOC} already exists. Would you like to overwrite it? (y/n)')
    userin = input().lower()
    if userin == 'y':
        DBLOC.unlink()
        createdb(scanpath)
    else:
        print('Exiting')


def statsdb():
    try:
        con, cur = opendb()

        record = cur.execute('SELECT COUNT(*) FROM songs')
        ttracks = cur.fetchone()[0]
        record = cur.execute('SELECT SUM(length) FROM songs')
        tlength = str(datetime.timedelta(seconds=cur.fetchone()[0]))

        lmod = datetime.datetime.fromtimestamp(int(DBLOC.stat().st_mtime))

        print(
            f'\nDatabase Stats'
            f'\nTracks: {ttracks}'
            f'\nTotal Length: {tlength}'
            f'\nLast modified: {lmod}'
        )
    except sqlite3.Error as error:
        print('DB Error:', error)
    finally:
        con.close()


if __name__ == '__main__':
    pass
