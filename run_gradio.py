import subprocess, sys, os, signal, time

env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
proc = subprocess.Popen(
    [sys.executable, '-X', 'utf8', 'app.py'],
    cwd='D:/Projects/my-langchain-agent',
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=env,
)

# Wait up to 15 seconds for startup
start = time.time()
while time.time() - start < 15:
    line = proc.stdout.readline()
    if line:
        print(line.decode('utf-8', errors='replace').strip())
        if 'http' in line.decode('utf-8', errors='replace').lower() or 'running' in line.decode('utf-8', errors='replace').lower():
            break
    else:
        time.sleep(0.5)

# Keep reading for 3 more seconds
time.sleep(3)
remaining = proc.stdout.read(1024)
if remaining:
    print(remaining.decode('utf-8', errors='replace'))

proc.terminate()
proc.wait()
