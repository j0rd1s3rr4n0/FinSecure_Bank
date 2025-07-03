import subprocess
import sys
import time
from threading import Thread

# Initialize DB
subprocess.check_call([sys.executable, 'init_db.py'])

# Start internal server
internal = subprocess.Popen([sys.executable, 'app_internal.py'])
# Give it a moment to start
time.sleep(1)

# Start public server
public = subprocess.Popen([sys.executable, 'app_public.py'])

try:
    internal.wait()
    public.wait()
except KeyboardInterrupt:
    internal.terminate()
    public.terminate()
