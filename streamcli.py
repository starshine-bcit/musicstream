import streamio
import pathlib
import argparse


def main():
    parser = argparse.ArgumentParser(description="Music Database Management and Server")

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
        default = pathlib.Path('./logs')
    )
    parser.add_argument(
        '-c',
        '--cert',
        type = pathlib.Path,
        help = 'certificate to load (default ./cert/certificate.txt)',
        default = pathlib.Path('./cert/certificate.txt')
    )
    parser.add_argument(
        '-h',
        '--host',
        type = str,
        help = 'IP address of server (default 127.0.0.1)',
        default = '127.0.0.1'
    )
    parser.add_argument(
        '-p',
        '--port',
        type = int,
        help = 'remote port to connect on, 50000+ (default 58743)',
        default = 58743
    )
    parser.add_argument(
        '--secrets',
        type = pathlib.Path,
        help = 'log secrets to a specified file, for debugging with wireshark'
    )

    args = parser.parse_args()

    print(args)



if __name__ == '__main__':
    main()