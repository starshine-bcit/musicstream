from typing import Dict, Optional
import logging
import pathlib
import asyncio
from construct import *

from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from aioquic.quic.logger import QuicFileLogger
from aioquic.tls import SessionTicket


class queryprot(QuicConnectionProtocol):
    def __init__(self, logger):
        self.cmdb = PaddedString(8, 'utf8')
        self.logger = logger
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

    def quic_event_received(self, event: QuicEvent):
        if isinstance(event, StreamDataReceived):
            #unpack recieved data and print
            count, cmd, data = self.unpack(event.data)
            self.logger.debug(f'Data recieved: {count}, {cmd}, {data}')

            #repack data and send it back
            retquery = self.pack(cmd, data)
            self._quic.send_stream_data(event.stream_id, retquery, end_stream=True)

class SessionTicketStore:
    def __init__(self):
        self.tickets: Dict[bytes, SessionTicket] = {}

    def add(self, ticket:SessionTicket):
        self.tickets[ticket.ticket] = ticket

    def pop(self, label: bytes):
        return self.tickets.pop(label, None)


def initio(args):

    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    logger = QuicFileLogger(args.log)

    if args.secrets:
        secrets = pathlib.Path('./logs/secrets')
        secrets_log_file = pathlib.Path.open(secrets, 'a')
    else:
        secrets_log_file = None

    conf = QuicConfiguration(
        is_client = False,
        quic_logger = logger,
        secrets_log_file=secrets_log_file
    )

    conf.load_cert_chain(args.cert, args.key)

    tstore = SessionTicketStore()

    return conf, tstore, logger


def listen(conf, tstore, logger, args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        serve(
            args.interface,
            args.port,
            configuration=conf,
            create_protocol=queryprot(logger),
            session_ticket_fetcher=tstore.pop,
            session_ticket_handler=tstore.add,
            retry=args.retry,
        )
    )
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


def close(logger, conf, tstore):
    pass

if __name__ == '__main__':
    pass
