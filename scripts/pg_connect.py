import os
import sys
from pathlib import Path

def load_env(path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())


ROOT = Path(__file__).resolve().parent.parent
load_env(ROOT / '.env')

host = os.getenv('DATABASE_HOST')
port = os.getenv('DATABASE_PORT', '5432')
dbname = os.getenv('DATABASE_NAME', 'postgres')
user = os.getenv('DATABASE_USER', 'postgres')
password = os.getenv('DATABASE_PASSWORD')
sslmode = os.getenv('DATABASE_SSLMODE', 'require')

print('Attempting psycopg2 connection to', host, 'port', port)

try:
    import psycopg2
except Exception as e:
    print('psycopg2 import failed:', e)
    sys.exit(3)

try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, sslmode=sslmode, connect_timeout=5)
    print('CONNECTED OK')
    conn.close()
    sys.exit(0)
except Exception as e:
    print('CONNECT FAILED:', repr(e))
    sys.exit(2)
