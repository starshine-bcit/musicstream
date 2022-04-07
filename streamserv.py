
import pathlib
import argparse
import streamdb
import streamio


DBLOC = pathlib.Path('streamserv.db')

# General ToDo:
#
# aioquic for networking
# protocol buffer (google)
# error handling
# add poetry
#


def main():
    parser = argparse.ArgumentParser(description='Music Database Management and Server')

    parser.add_argument(
        'run',
        type = str,
        help = '"db" will interact with database, "serv" will start the server'
    )

    dbgroup = parser.add_mutually_exclusive_group()
    dbgroup.add_argument(
        '-create',
        action = 'store_true',
        help = 'create our streamserv.db database'
    )
    dbgroup.add_argument(
        '-update',
        action = 'store_true',
        help = 'update our database (not currently implemented)'
    )
    dbgroup.add_argument(
        '-stats',
        action = 'store_true',
        help = 'print some basic stats about our database'
    )

    parser.add_argument(
        '-d',
        '--directory',
        type = pathlib.Path,
        help = 'absolute path to your mp3 library'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action = 'store_true',
        help = 'enable verbose quic logging'
    )
    parser.add_argument(
        '-l',
        '--log',
        type = pathlib.Path,
        help = 'log quic events to a specified log file (defaults ./log)',
        default = pathlib.Path('./logs/client')
    )
    parser.add_argument(
        '-c',
        '--cert',
        type = pathlib.Path,
        help = 'certificate to load (default ./cert/certificate.txt)',
        default = pathlib.Path('./cert/certificate.txt')
    )
    parser.add_argument(
        '-k',
        '--key',
        type = pathlib.Path,
        help = 'private key file to load (default ./cert/private_key.txt)',
        default = pathlib.Path('./cert/private_key.txt')
    )
    parser.add_argument(
        '-p',
        '--port',
        type = int,
        help = 'port to listen on, 50000+ (default 58743)',
        default = 58743
    )
    parser.add_argument(
        '-i',
        '--interface',
        type = str,
        help = 'interface to listen on (default "::" = all)',
        default = '::'
    )
    parser.add_argument(
        '-r',
        '--retry',
        action = 'store_true',
        default = False,
        help = 'send a retry for connections (default False)'
    )
    parser.add_argument(
        '--secrets',
        action = 'store_true',
        default = False,
        help = 'logs secrets to /logs/secrets, for debugging with wireshark'
    )

    args = parser.parse_args()

    print(args)

    if args.run == 'db':
        if args.create:
            if args.path.exists() and args.path.is_absolute():
                if DBLOC.is_file:
                    streamdb.recreatedb(args.path)
                else:
                    streamdb.createdb(args.path)
        elif args.update:
            pass
        elif args.stats:
            if pathlib.Path.is_file(DBLOC):
                streamdb.statsdb()
            else:
                print(f'Error: You cannot have database stats without a {DBLOC}')
    elif args.run == 'serv':
        conf, tstore, logger = streamio.initio(args)
        print('Initialization successfull, starting to listen...')
        streamio.listen(conf, tstore, logger, args)


if __name__ == '__main__':
    main()
