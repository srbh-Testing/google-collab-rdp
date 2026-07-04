import os
import subprocess
import time
import requests

username = "user"
password = "root"

os.system("fuser -k 6080/tcp 5900/tcp 4040/tcp 2>/dev/null")
os.system("killall -9 Xvfb x11vnc websockify firefox qbittorrent telegram-desktop ngrok 2>/dev/null")
time.sleep(1)

os.system(f"useradd -m {username} 2>/dev/null")
os.system(f"adduser {username} sudo 2>/dev/null")
os.system(f"echo '{username}:{password}' | sudo chpasswd")
os.system("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")

os.system("apt update -qq")
os.system("DEBIAN_FRONTEND=noninteractive apt install -y xfce4 xfce4-terminal dbus-x11 aria2 wget curl qbittorrent x11vnc xvfb novnc websockify -qq")

os.system("wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O /etc/apt/keyrings/packages.mozilla.org.asc")
os.system('echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee /etc/apt/sources.list.d/mozilla.list')
os.system('echo \'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\' | tee /etc/apt/preferences.d/mozilla')
os.system("apt update -qq && DEBIAN_FRONTEND=noninteractive apt install -y firefox -qq")

os.makedirs("/root/.config/xfce4/xfconf/xfce-perchannel-xml/", exist_ok=True)
with open("/root/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml", "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?><channel name="xfwm4" version="1.0"><property name="general" type="empty"><property name="use_compositing" type="bool" value="false"/></property></channel>')

subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1280x720x16', '-ac'])
while not os.path.exists("/tmp/.X11-unix/X99"):
    time.sleep(0.2)

custom_env = os.environ.copy()
custom_env['DISPLAY'] = ':99'
subprocess.Popen(['dbus-launch', 'startxfce4'], env=custom_env)
time.sleep(3)

subprocess.Popen(['qbittorrent'], env=custom_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2) 
subprocess.Popen(['firefox'], env=custom_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

subprocess.Popen(['x11vnc', '-display', ':99', '-forever', '-nopw', '-quiet', '-listen', 'localhost', '-defer', '0', '-threads'])
time.sleep(1)
subprocess.Popen(['websockify', '--web', '/usr/share/novnc/', '6080', 'localhost:5900'], stdout=subprocess.DEVNULL)
time.sleep(1)

os.system("curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
os.system('echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list')
os.system("apt update -qq && apt install ngrok -qq")

os.system("ngrok config add-authtoken 2NbeU8pX67V1pL7kG3yLp9rXWz9_6qg7Gv3X9b8z7y6w5v4u3")
subprocess.Popen(['ngrok', 'http', '6080'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(7)

try:
    res = requests.get("http://localhost:4040/api/tunnels").json()
    ngrok_url = res['tunnels'][0]['public_url'].replace("http://", "https://")
    ngrok_link = f"{ngrok_url}/vnc.html?autoconnect=true&resize=scale"
except Exception:
    ngrok_link = "Tunnel Failed. Please Restart Session."

print("\n" + "="*60)
print("🔥 FIXED BROWSER VNC ONLINE (NO PASSWORD NEEDED) 🔥")
print("="*60)
print(f"🔗 CLICK THIS LINK:\n👉 {ngrok_link}")
print("="*60)
print("\n🛡️ ANTI-DISCONNECT ACTIVE")

count = 0
while True:
    time.sleep(30)
    count += 30
    print(f"✨ Session Keep-Alive Status: Active ({count}s elapsed)")
    
