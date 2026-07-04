import os
import subprocess
import time
import re

print("🧹 1. Clearing ports and residual background processes...")
os.system("fuser -k 6080/tcp 5900/tcp 2>/dev/null")
os.system("killall -9 Xvfb x11vnc websockify firefox qbittorrent cloudflared 2>/dev/null")
time.sleep(1)

print("🔄 2. Installing core components and standard environments...")
os.system("apt update -qq")
os.system("DEBIAN_FRONTEND=noninteractive apt install -y xfce4 xfce4-terminal dbus-x11 aria2 wget curl qbittorrent x11vnc xvfb novnc websockify -qq")

print("📦 3. Setting up stable Firefox browser repository...")
os.system("wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O /etc/apt/keyrings/packages.mozilla.org.asc")
os.system('echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee /etc/apt/sources.list.d/mozilla.list')
os.system('echo \'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\' | tee /etc/apt/preferences.d/mozilla')
os.system("apt update -qq && DEBIAN_FRONTEND=noninteractive apt install -y firefox -qq")

os.makedirs("/root/.config/xfce4/xfconf/xfce-perchannel-xml/", exist_ok=True)
with open("/root/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml", "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?><channel name="xfwm4" version="1.0"><property name="general" type="empty"><property name="use_compositing" type="bool" value="false"/></property></channel>')

print("🚀 4. Booting virtual X11 graphics screen buffer...")
subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1280x720x16', '-ac'])
while not os.path.exists("/tmp/.X11-unix/X99"):
    time.sleep(0.2)

custom_env = os.environ.copy()
custom_env['DISPLAY'] = ':99'
subprocess.Popen(['dbus-launch', 'startxfce4'], env=custom_env)
time.sleep(3)

print("📦 5. Launching Firefox and system applications...")
subprocess.Popen(['qbittorrent'], env=custom_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
subprocess.Popen(['firefox'], env=custom_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

print("🔌 6. Turning on VNC to HTML5 Websockify translation layer...")
subprocess.Popen(['x11vnc', '-display', ':99', '-forever', '-nopw', '-quiet', '-listen', 'localhost', '-defer', '0', '-threads'])
time.sleep(1)
subprocess.Popen(['websockify', '--web', '/usr/share/novnc/', '6080', 'localhost:5900'], stdout=subprocess.DEVNULL)
time.sleep(1)

print("🌐 7. Deploying Cloudflare Secure Proxy Engine...")
os.system("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared")
os.system("chmod +x /usr/local/bin/cloudflared")

# Log file capture fix
log_path = "cf.log"
if os.path.exists(log_path):
    os.remove(log_path)

log_file = open(log_path, "w")
subprocess.Popen(['cloudflared', 'tunnel', '--url', 'http://localhost:6080'], stdout=log_file, stderr=log_file)

print("\n⏱️ Waiting for Cloudflare network handshake...")
final_link = None

# Loop to dynamically wait and fetch link as soon as it's ready
for _ in range(6):
    time.sleep(5)
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log_content = f.read()
        urls = re.findall(r'https://[-0-9a-z.]+\.trycloudflare\.com', log_content)
        if urls:
            final_link = f"{urls[0]}/vnc.html?autoconnect=true&resize=scale"
            break
    print("⏳ Retrying tunnel lookup...")

print("\n" + "="*70)
if final_link:
    print("🔥 BROWSER VNC SYSTEM ONLINE (noVNC Portal Ready) 🔥")
    print("="*70)
    print(f"🔗 CLICK THIS LINK:\n👉 {final_link}")
else:
    print("❌ Link parsing delayed. Printing raw logs below. Look for the .trycloudflare.com link:")
    print("="*70)
    os.system("cat cf.log | grep trycloudflare.com")
print("="*70)

print("\n🛡️ ANTI-DISCONNECT ACTIVATED: Active keep-alive terminal logs online.")
count = 0
while True:
    time.sleep(30)
    count += 30
    print(f"✨ Session Keep-Alive Status: Active ({count}s elapsed)")
    
