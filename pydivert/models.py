# -*- coding: utf-8 -*-
# Copyright (C) 2013  Fabio Falcinelli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from binascii import unhexlify, hexlify
import socket
import ctypes

from pydivert import enum
from pydivert.enum import Direction
from pydivert.winutils import string_to_addr, addr_to_string


__author__ = 'fabio'


def format_structure(instance):
    """
    Return a string representation for the structure
    """
    if hasattr(instance, "_fields_"):
        out = []
        for field in instance._fields_:
            out.append("[%s: %s]" % (field[0], getattr(instance, field[0], None)))
        return "".join(out)
    else:
        raise ValueError("Passed argument is not a structure!")

class WinDivertAddress(ctypes.Structure):
    """
    Ctypes Structure for WINDIVERT_ADDRESS.
    The WINDIVERT_ADDRESS structure represents the "address" of a captured or injected packet.
    The address includes the packet's network interfaces and the packet direction.

    typedef struct
    {
        UINT32 IfIdx;
        UINT32 SubIfIdx;
        UINT8  Direction;
    } WINDIVERT_ADDRESS, *PWINDIVERT_ADDRESS;

    Fields:

        - IfIdx: The interface index on which the packet arrived (for inbound packets), or is to be sent (for outbound packets).
        - SubIfIdx: The sub-interface index for IfIdx.
        - Direction: The packet's direction. The possible values are
                    - WINDIVERT_DIRECTION_OUTBOUND with value 0 for outbound packets.
                    - WINDIVERT_DIRECTION_INBOUND with value 1 for inbound packets.
    """
    _fields_ = [("IfIdx", ctypes.c_uint32),
                ("SubIfIdx", ctypes.c_uint32),
                ("Direction", ctypes.c_uint8)]

    def __str__(self):
        return format_structure(self)


class DivertIpHeader(ctypes.Structure):
    """
    Ctypes structure for WINDIVERT_IPHDR: IPv4 header definition.

    typedef struct
    {
        UINT8  HdrLength:4;
        UINT8  Version:4;
        UINT8  TOS;
        UINT16 Length;
        UINT16 Id;
        UINT16 ...;
        UINT8  TTL;
        UINT8  Protocol;
        UINT16 Checksum;
        UINT32 SrcAddr;
        UINT32 DstAddr;
    } WINDIVERT_IPHDR, *PWINDIVERT_IPHDR;
    """
    _fields_ = [("HdrLength", ctypes.c_uint8, 4),
                ("Version", ctypes.c_uint8, 4),
                ("TOS", ctypes.c_uint8),
                ("Length", ctypes.c_uint16),
                ("Id", ctypes.c_uint16),
                ("FragOff0", ctypes.c_uint16),
                ("TTL", ctypes.c_uint8),
                ("Protocol", ctypes.c_uint8),
                ("Checksum", ctypes.c_uint16),
                ("SrcAddr", ctypes.c_uint32),
                ("DstAddr", ctypes.c_uint32), ]

    def __str__(self):
        return format_structure(self)


class DivertIpv6Header(ctypes.Structure):
    """
    Ctypes structure for WINDIVERT_IPV6HDR: IPv6 header definition.

    UINT8  TrafficClass0:4;
    UINT8  Version:4;
    UINT8  FlowLabel0:4;
    UINT8  TrafficClass1:4;
    UINT16 FlowLabel1;

    typedef struct
    {
        UINT32 Version:4;
        UINT32 ...:28;
        UINT16 Length;
        UINT8  NextHdr;
        UINT8  HopLimit;
        UINT32 SrcAddr[4];
        UINT32 DstAddr[4];
    } WINDIVERT_IPV6HDR, *PWINDIVERT_IPV6HDR;
    """
    _fields_ = [("TrafficClass0", ctypes.c_uint8, 4),
                ("Version", ctypes.c_uint8, 4),
                ("FlowLabel0", ctypes.c_uint8, 4),
                ("TrafficClass1", ctypes.c_uint8, 4),
                ("FlowLabel1", ctypes.c_uint16, 4),
                ("Length", ctypes.c_uint16),
                ("NextHdr", ctypes.c_uint8),
                ("HopLimit", ctypes.c_uint8),
                ("SrcAddr", ctypes.c_uint32 * 4),
                ("DstAddr", ctypes.c_uint32 * 4), ]

    def __str__(self):
        return format_structure(self)


class DivertIcmpHeader(ctypes.Structure):
    """
    Ctypes structure for WINDIVERT_ICMPHDR: ICMP header definition.

    typedef struct
    {
        UINT8  Type;
        UINT8  Code;
        UINT16 Checksum;
        UINT32 Body;
    } WINDIVERT_ICMPHDR, *PWINDIVERT_ICMPHDR;
    """
    _fields_ = [("Type", ctypes.c_uint8),
                ("Code", ctypes.c_uint8),
                ("Checksum", ctypes.c_uint16),
                ("Body", ctypes.c_uint32)]

    def __str__(self):
        return format_structure(self)


class DivertIcmpv6Header(ctypes.Structure):
    """
    Ctypes structure for WINDIVERT_IPV6HDR: ICMPv6 header definition.

    typedef struct
    {
        UINT8  Type;
        UINT8  Code;
        UINT16 Checksum;
        UINT32 Body;
    } WINDIVERT_ICMPV6HDR, *PWINDIVERT_ICMPV6HDR;
    """
    _fields_ = [("Type", ctypes.c_uint8),
                ("Code", ctypes.c_uint8),
                ("Checksum", ctypes.c_uint16),
                ("Body", ctypes.c_uint32)]

    def __str__(self):
        return format_structure(self)


class DivertTcpHeader(ctypes.Structure):
    """
    Ctypes structure for WINDIVERT_TCPHDR: TCP header definition.

    typedef struct
    {
        UINT16 SrcPort;
        UINT16 DstPort;
        UINT32 SeqNum;
        UINT32 AckNum;
        UINT16 Reserved1:4;
        UINT16 HdrLength:4;
        UINT16 Fin:1;
        UINT16 Syn:1;
        UINT16 Rst:1;
        UINT16 Psh:1;
        UINT16 Ack:1;
        UINT16 Urg:1;
        UINT16 Reserved2:2;
        UINT16 Window;
        UINT16 Checksum;
        UINT16 UrgPtr;
    } WINDIVERT_TCPHDR, *PWINDIVERT_TCPHDR;
    """
    _fields_ = [("SrcPort", ctypes.c_uint16),
                ("DstPort", ctypes.c_uint16),
                ("SeqNum", ctypes.c_uint32),
                ("AckNum", ctypes.c_uint32),
                ("Reserved1", ctypes.c_uint16, 4),
                ("HdrLength", ctypes.c_uint16, 4),
                ("Fin", ctypes.c_uint16, 1),
                ("Syn", ctypes.c_uint16, 1),
                ("Rst", ctypes.c_uint16, 1),
                ("Psh", ctypes.c_uint16, 1),
                ("Ack", ctypes.c_uint16, 1),
                ("Urg", ctypes.c_uint16, 1),
                ("Reserved2", ctypes.c_uint16, 2),
                ("Window", ctypes.c_uint16),
                ("Checksum", ctypes.c_uint16),
                ("UrgPtr", ctypes.c_uint16), ]

    def __str__(self):
        return format_structure(self)


class DivertUdpHeader(ctypes.Structure):
    """
    Ctypes structure for WINDIVERT_UDPHDR: UDP header definition.

    typedef struct
    {
        UINT16 SrcPort;
        UINT16 DstPort;
        UINT16 Length;
        UINT16 Checksum;
    } WINDIVERT_UDPHDR, *PWINDIVERT_UDPHDR;
    """
    _fields_ = [("SrcPort", ctypes.c_uint16),
                ("DstPort", ctypes.c_uint16),
                ("Length", ctypes.c_uint16),
                ("Checksum", ctypes.c_uint16)]

    def __str__(self):
        return format_structure(self)


headers_map = {"ipv4_hdr": DivertIpHeader,
               "ipv6_hdr": DivertIpv6Header,
               "tcp_hdr": DivertTcpHeader,
               "udp_hdr": DivertUdpHeader,
               "icmp_hdr": DivertIcmpHeader,
               "icmpv6_hdr": DivertIcmpv6Header}


class HeaderWrapper(object):
    """
    Since there's no "Options" field in the header structs, we use this wrapper
    to carry the "Options" field if available.

    Any field requested to an instance of this class is delegated to the original
    header, except the "Options" one.
    """

    def __init__(self, hdr, opts='', encoding="UTF-8"):
        self.hdr, self.opts = hdr, opts
        self.encoding = encoding

        for name, clazz in headers_map.items():
            if isinstance(hdr, clazz):
                self.type = name.split("_")[0]

    def __getattr__(self, item):
        if item != "hdr" and hasattr(self.hdr, item):
            return getattr(self.hdr, item)
        elif item == "Options":
            return self.opts if self.opts else ''
        else:
            return super(HeaderWrapper, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if key != "hdr" and hasattr(self.hdr, key):
            setattr(self.hdr, key, value)
        elif key == "Options":
            self.opts = value if value else ''
        else:
            return super(HeaderWrapper, self).__setattr__(key, value)

    @property
    def raw(self):
        hexed = hexlify(self.hdr)
        if self.opts:
            hexed += hexlify(self.opts)
        hdr_len = getattr(self, "HdrLength", 0) * 4
        if (len(hexed) / 2) < hdr_len:
            hexed += b"00" * (hdr_len - len(hexed) / 2)
        return hexed

    def __repr__(self):
        return self.raw.decode(self.encoding)

    def __str__(self):
        return "%s Header: %s [Options: %s]" % (self.type.title(),
                                                self.hdr,
                                                hexlify(self.opts) if self.opts else '')


class CapturedMetadata(object):
    """
    Captured metadata on interface and flow direction
    """

    def __init__(self, iface, direction):
        self.iface = iface
        self.direction = direction

    def is_outbound(self):
        return self.direction == Direction.OUTBOUND

    def is_inbound(self):
        return self.direction == enum.Direction.INBOUND

    def is_loopback(self):
        return self.iface[0] == 1

    def __str__(self):
        return "Interface: (Index: %s, SubIndex %s) Flow: %s" % (self.iface[0],
                                                                 self.iface[1],
                                                                 "outbound" if self.direction != 1 else "inbound")


class CapturedPacket(object):
    """
    Gathers several network layers of data
    """

    def __init__(self, headers, payload=None, raw_packet=None, meta=None, encoding="UTF-8"):
        if len(headers) > 2:
            raise ValueError("No more than 2 headers (tcp/udp/icmp over ip) are supported")

        self.payload = payload
        self._raw_packet = raw_packet
        self.meta = meta

        self.headers = [None, None]
        self.headers_opt = [None, None]
        for header in headers:
            if type(header.hdr) in (DivertIpHeader, DivertIpv6Header):
                self.headers[0] = header
            else:
                self.headers[1] = header
        self.encoding = encoding

    def _get_from_headers(self, key):
        for header in self.headers:
            if hasattr(header, key):
                return header, getattr(header, key, None)
        return None, None

    def _set_in_headers(self, key, value):
        for header in self.headers:
            if hasattr(header, key):
                setattr(header, key, value)
                break

    @property
    def address_family(self):
        for v6hdr in ("ipv6_hdr", "icmpv6_hdr"):
            if getattr(self, v6hdr):
                return socket.AF_INET6
        return socket.AF_INET

    @property
    def src_port(self):
        header, src_port = self._get_from_headers("SrcPort")
        if src_port:
            return socket.htons(src_port)

    @src_port.setter
    def src_port(self, value):
        self._set_in_headers("SrcPort", socket.ntohs(value))

    @property
    def dst_port(self):
        header, dst_port = self._get_from_headers("DstPort")
        if dst_port:
            return socket.htons(dst_port)

    @dst_port.setter
    def dst_port(self, value):
        self._set_in_headers("DstPort", socket.ntohs(value))

    @property
    def src_addr(self):
        header, src_addr = self._get_from_headers("SrcAddr")
        if src_addr:
            return addr_to_string(self.address_family, src_addr, self.encoding)

    @src_addr.setter
    def src_addr(self, value):
        self._set_in_headers("SrcAddr", string_to_addr(self.address_family, value, self.encoding))

    @property
    def dst_addr(self):
        header, dst_addr = self._get_from_headers("DstAddr")
        if dst_addr:
            return addr_to_string(self.address_family, dst_addr, self.encoding)

    @dst_addr.setter
    def dst_addr(self, value):
        self._set_in_headers("DstAddr", string_to_addr(self.address_family, value, self.encoding))

    def __getattr__(self, item):
        clazz = headers_map.get(item, None)
        if clazz:
            for header in self.headers:
                if isinstance(header.hdr, clazz):
                    return header
        else:
            return super(CapturedPacket, self).__getattribute__(item)

    def __setattr__(self, key, value):
        clazz = headers_map.get(key, None)
        if clazz:
            if key in ("ipv4_hdr", "ipv6_hdr"):
                self.headers[0].hdr = value
            else:
                self.headers[1].hdr = value
        else:
            super(CapturedPacket, self).__setattr__(key, value)

    @property
    def raw(self):
        hexed = b"".join([header.raw for header in self.headers])
        if self.payload:
            hexed += hexlify(self.payload)
        return unhexlify(hexed)

    def __repr__(self):
        return hexlify(self.raw).decode(self.encoding)

    def __str__(self):
        tokens = list()
        tokens.append("Packet: %s:%s --> %s:%s" % (self.src_addr,
                                                   self.src_port,
                                                   self.dst_addr,
                                                   self.dst_port))
        if self.meta:
            tokens.append(str(self.meta))
        tokens.extend([str(hdr) for hdr in self.headers])
        tokens.append("Payload: [%s] [HEX: %s]" % (self.payload,
                                                   hexlify(self.payload) if self.payload else ''))
        return "\n".join(tokens)
