import argparse
import asyncio
import logging
import pickle
import ssl
from typing import Optional, cast
from construct import *
import pathlib

from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from aioquic.quic.logger import QuicFileLogger

logger = logging.getLogger("client")


class queryprot(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self._ack_waiter: Optional[asyncio.Future[DNSRecord]] = None
        self.cmdb = PaddedString(8, 'utf8')
        self.qprot = Struct(
            'count' / Int16ul,
            'cmd' / Bytes(8),
            'data' / Bytes(lambda this: this.count - this._subcons.cmd.sizeof() - this._subcons.count.sizeof())
        )
    def pack(self, cmd, output):
        count = len(output) + 10
        cmd = self.cmdb.build(cmd)
        return self.qprot.build(dict(count=count, cmd=cmd, data=output))

    def unpack(self, input):
        upack = self.qprot.parse(input)
        count = upack['count']
        cmd = self.cmdb.parse(upack['cmd'])
        data = upack['data']
        return count, cmd , data

    async def query(self, cmd, data):
        query = self.pack(cmd, data)

        # send query and wait for answer
        stream_id = self._quic.get_next_available_stream_id()
        self._quic.send_stream_data(stream_id, query, end_stream=True)
        waiter = self._loop.create_future()
        self._ack_waiter = waiter
        self.transmit()

        return await asyncio.shield(waiter)

    def quic_event_received(self, event: QuicEvent):
        if self._ack_waiter is not None:
            if isinstance(event, StreamDataReceived):
                # parse answer
                count, cmd, data = self.unpack(event.data)
                print(count)
                print(cmd)
                print(data)
                # return answer
                #waiter = self._ack_waiter
                #self._ack_waiter = None
                #waiter.set_result(answer)


def save_session_ticket(ticket):
    logger.info("New session ticket received")
    if args.session_ticket:
        with open(args.session_ticket, "wb") as fp:
            pickle.dump(ticket, fp)


def initconfig(args):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    configuration = QuicConfiguration(is_client=True)
    if args.ca_certs:
        configuration.load_verify_locations(args.ca_certs)
    if args.insecure:
        configuration.verify_mode = ssl.CERT_NONE
    if args.quic_log:
        configuration.quic_logger = QuicFileLogger(args.quic_log)
    if args.secrets_log:
        secrets = pathlib.Path('./logs/secrets')
        configuration.secrets_log_file = pathlib.Path.open(secrets, 'a')
    if args.session_ticket:
        try:
            with open(args.session_ticket, "rb") as fp:
                configuration.session_ticket = pickle.load(fp)
        except FileNotFoundError:
            logger.debug(f"Unable to read {args.session_ticket}")
            pass
    else:
        logger.debug("No session ticket defined...")

    return configuration

async def run(
    configuration: QuicConfiguration,
    host,
    port,
    query_name,
    query_type,
):
    logger.debug(f'Connecting to {host}:{port}')
    async with connect(
        host,
        port,
        configuration=configuration,
        session_ticket_handler=save_session_ticket,
        create_protocol=queryprot,
    ) as client:
        client = cast(queryprot, client)
        logger.debug('Sending Test Data')
        answer = await client.query(query_name, query_type)
        logger.info(f'Recieved reply: \n{answer}')


def run_loop(config, args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run(
            configuration=config,
            host=args.host,
            port=args.port,
            message=args.message,
        )
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client size for streamserv.py')

    parser.add_argument(
        '-m',
        '--message',
        required = True,
        help = 'test data to send'
    )
    parser.add_argument(
        '-h'
        '--host',
        type = str,
        default = 'localhost',
        help = 'IP address or host name to connect with (default: localhost)',
    )
    parser.add_argument(
        '-p',
        '--port',
        type = int,
        default = 58743,
        help='Port number the server is listening on (default 58743)'
    )
    parser.add_argument(
        '-l',
        '--log',
        type = pathlib.Path,
        help = 'log quic events to a specified log file (defaults ./log)',
        default = pathlib.Path('./logs')
    )
    parser.add_argument(
        '--secrets',
        action = 'store_true',
        default = False,
        help = 'logs secrets to /logs/secrets, for debugging with wireshark'
    )
    parser.add_argument(
        '--insecure',
        action='store_true',
        default = False,
        help='do not validate server certificate'
    )
    # parser.add_argument(
    #     '--ca-certs',
    #     type=str,
    #     help='load CA certificates from the specified file'
    # )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable verbose quic logging"
    )
    # parser.add_argument(
    #     "-s",
    #     "--session-ticket",
    #     type=str,
    #     help="read and write session ticket from the specified file",
    # )
    args = parser.parse_args()

    config = initconfig(args)

    run_loop(config, args)

    