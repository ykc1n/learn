#!/usr/bin/env python3
"""Install a Linux user service using explicit private network settings."""
import argparse,ipaddress,os
from pathlib import Path
import subprocess,sys
parser=argparse.ArgumentParser()
parser.add_argument('--host',required=True,help='This computer\'s private IPv4 address')
parser.add_argument('--subnet',required=True,help='Allowed Wi-Fi subnet, for example 192.168.1.0/24')
parser.add_argument('--domain',default='nightspirit.xyz')
parser.add_argument('--port',type=int,default=8081)
args=parser.parse_args()
network=ipaddress.ip_network(args.subnet)
address=ipaddress.ip_address(args.host)
if address.version!=4 or not address.is_private or address.is_loopback or address not in network:
    parser.error('Host must be a private IPv4 address inside the subnet')
if not 1<=args.port<=65535:parser.error('Invalid port')
if not args.domain or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789.-' for c in args.domain):
    parser.error('Use a lowercase DNS hostname')
root=Path(__file__).resolve().parents[1]
if not (root/'dist/index.html').is_file():parser.error('Run npm ci and npm run build first')
(root/'data').mkdir(exist_ok=True)
def quoted(value):
    return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
unit=f'''[Unit]
Description=Nightspirit private LAN learning library
StartLimitIntervalSec=0

[Service]
ExecStart={quoted(sys.executable)} {quoted(root/'server.py')} --host {args.host} --port {args.port}
WorkingDirectory={quoted(root)}
Environment=NIGHTSPIRIT_SUBNET={network}
Environment=NIGHTSPIRIT_DOMAIN={args.domain}
Restart=on-failure
RestartSec=10
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths={quoted(root/'data')}
RestrictAddressFamilies=AF_INET AF_UNIX AF_NETLINK
UMask=0077

[Install]
WantedBy=default.target
'''
destination=Path.home()/'.config/systemd/user/nightspirit-learn.service'
destination.parent.mkdir(parents=True,exist_ok=True)
destination.write_text(unit)
subprocess.run(['systemctl','--user','daemon-reload'],check=True)
subprocess.run(['systemctl','--user','enable','nightspirit-learn'],check=True)
subprocess.run(['systemctl','--user','restart','nightspirit-learn'],check=True)
print(f'Local server: http://{args.host}:{args.port}')
