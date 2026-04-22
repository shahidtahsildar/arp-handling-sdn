from pox.core import core
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class ARPHandler(object):
    def __init__(self):
        self.arp_table = {}
        self.mac_to_port = {}
        core.openflow.addListeners(self)
        log.info("ARP Handler Controller Started")

    def _handle_ConnectionUp(self, event):
        log.info("Switch connected: %s", event.dpid)

    def _handle_PacketIn(self, event):
        pkt = event.parsed
        if not pkt.parsed:
            return
        dpid = event.dpid
        in_port = event.port
        src_mac = str(pkt.src)
        dst_mac = str(pkt.dst)

        # Learn MAC -> port
        self.mac_to_port[(dpid, src_mac)] = in_port

        # Handle ARP
        arp_pkt = pkt.find('arp')
        if arp_pkt:
            self.handle_arp(event, arp_pkt, dpid, in_port)
            return

        # Handle all other packets (L2 forwarding)
        key = (dpid, dst_mac)
        if key in self.mac_to_port:
            out_port = self.mac_to_port[key]
            log.info("Forwarding packet from %s to %s on port %s", src_mac, dst_mac, out_port)
            # Install a flow rule
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(pkt, in_port)
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.data = event.ofp
            event.connection.send(msg)
        else:
            # Flood if we don't know the destination
            log.info("Unknown destination %s, flooding", dst_mac)
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            event.connection.send(msg)

    def handle_arp(self, event, arp_pkt, dpid, in_port):
        src_ip = str(arp_pkt.protosrc)
        src_mac = str(arp_pkt.hwsrc)
        dst_ip = str(arp_pkt.protodst)

        self.arp_table[src_ip] = src_mac
        log.info("ARP Table updated: %s -> %s", src_ip, src_mac)

        if arp_pkt.opcode == arp.REQUEST:
            log.info("ARP REQUEST: Who has %s? Tell %s", dst_ip, src_ip)
            if dst_ip in self.arp_table:
                dst_mac = self.arp_table[dst_ip]
                log.info("Controller replying: %s is at %s", dst_ip, dst_mac)
                self.send_arp_reply(event, src_ip, src_mac, dst_ip, dst_mac, in_port)
            else:
                log.info("MAC unknown, flooding ARP request")
                self.flood(event)

        elif arp_pkt.opcode == arp.REPLY:
            log.info("ARP REPLY: %s is at %s", src_ip, src_mac)
            dst_mac = str(arp_pkt.hwdst)
            key = (dpid, dst_mac)
            if key in self.mac_to_port:
                out_port = self.mac_to_port[key]
                self.send_packet(event, out_port)
            else:
                self.flood(event)

    def send_arp_reply(self, event, src_ip, src_mac, dst_ip, dst_mac, in_port):
        arp_reply = arp()
        arp_reply.opcode = arp.REPLY
        arp_reply.hwsrc = EthAddr(dst_mac)
        arp_reply.hwdst = EthAddr(src_mac)
        arp_reply.protosrc = IPAddr(dst_ip)
        arp_reply.protodst = IPAddr(src_ip)

        eth = ethernet()
        eth.type = ethernet.ARP_TYPE
        eth.src = EthAddr(dst_mac)
        eth.dst = EthAddr(src_mac)
        eth.payload = arp_reply

        msg = of.ofp_packet_out()
        msg.data = eth.pack()
        msg.actions.append(of.ofp_action_output(port=in_port))
        event.connection.send(msg)
        log.info("ARP Reply sent: %s is at %s", dst_ip, dst_mac)

    def flood(self, event):
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)

    def send_packet(self, event, out_port):
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(msg)

def launch():
    core.registerNew(ARPHandler)
