import socket
import sys

HOST = 'db.chffbwcfppmyheajddrs.supabase.co'
PORT = 5432

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    sock.connect((HOST, PORT))
    print('CONNECTED')
    sock.close()
    sys.exit(0)
except Exception as e:
    print('FAILED:', e)
    sys.exit(2)
