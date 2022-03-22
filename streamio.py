from typing import Dict, Optional
import logging
import pathlib
import asyncio
import struct

from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from aioquic.quic.logger import QuicFileLogger
from aioquic.tls import SessionTicket


class queryprot(QuicConnectionProtocol):
    def quic_event_received(self, event: QuicEvent):
        if isinstance(event, StreamDataReceived):
            # parse query
            query = struct.unpack('!c', bytes(event.data))[0]
            #query = DNSRecord.parse(event.data[2 : 2 + length])

            # perform lookup and serialize answer
            #data = query.send('where to send', 53)
            data = struct.pack("!H", len(data)) + data

            # send answer
            self._quic.send_stream_data(event.stream_id, data, end_stream=True)
    def parse(self, data):
        pass

        # from construct import *
    
    # myPascalString = Struct(
    #     "length" / Int8ul,
    #     "data" / Bytes(lambda ctx: ctx.length)
    # )

    # >>> myPascalString.parse(b'\x05helloXXX')
    # Container(length=5, data=b'hello')
    # >>> myPascalString.build(Container(length=6, data=b"foobar"))
    # b'\x06foobar'


    # myPascalString2 = ExprAdapter(myPascalString,
    #     encoder=lambda obj, ctx: Container(length=len(obj), data=obj),
    #     decoder=lambda obj, ctx: obj.data
    # )

    # >>> myPascalString2.parse(b"\x05hello")
    # b'hello'

    # >>> myPascalString2.build(b"i'm a long string")
    # b"\x11i'm a long string"

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
        secrets_log_file = pathlib.Path.open(args.secrets, 'a')
    else:
        secrets_log_file = None

    conf = QuicConfiguration(
        is_client = False,
        quic_logger = logger,
        secrets_log_file=secrets_log_file
    )

    conf.load_cert_chain(args.cert, args.key)

    tstore = SessionTicketStore()

    return conf, tstore


def listen(conf, tstore, args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        serve(
            args.interface,
            args.port,
            configuration=conf,
            create_protocol=queryprot,
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
