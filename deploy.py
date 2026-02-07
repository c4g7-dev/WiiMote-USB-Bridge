"""Deploy wiimote_bridge.py and setup_usb_gadget.sh to the Pi and restart services."""
import paramiko
import sys

PI_HOST = "192.168.0.64"
PI_USER = "pi"
PI_PASS = "pi"

FILES_TO_DEPLOY = [
    ("wiimote_bridge.py", "/opt/wiimote-bridge/wiimote_bridge.py"),
    ("scripts/setup_usb_gadget.sh", "/opt/wiimote-bridge/setup_usb_gadget.sh"),
    ("scripts/teardown_usb_gadget.sh", "/opt/wiimote-bridge/teardown_usb_gadget.sh"),
]


def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(PI_HOST, username=PI_USER, password=PI_PASS, timeout=10)

    # Upload files via SFTP
    sftp = client.open_sftp()
    for local, remote in FILES_TO_DEPLOY:
        tmp = f"/tmp/{local.replace('/', '_')}"
        print(f"Uploading {local} ...")
        sftp.put(local, tmp)
    sftp.close()
    print("Upload complete.")

    # Copy to install dirs and restart
    commands = []
    for local, remote in FILES_TO_DEPLOY:
        tmp = f"/tmp/{local.replace('/', '_')}"
        commands.append(f"cp {tmp} {remote}")
    commands.append("chmod 755 /opt/wiimote-bridge/*.sh")
    commands.append("systemctl restart wiimote-bridge")

    for cmd in commands:
        full_cmd = f"echo '{PI_PASS}' | sudo -S {cmd}"
        print(f"Running: sudo {cmd}")
        stdin, stdout, stderr = client.exec_command(full_cmd, timeout=30)
        out = stdout.read().decode()
        err = stderr.read().decode()
        rc = stdout.channel.recv_exit_status()
        if out.strip():
            print(f"  {out.strip()}")
        if rc != 0:
            err_clean = "\n".join(
                l for l in err.splitlines() if "[sudo]" not in l
            )
            if err_clean.strip():
                print(f"  stderr: {err_clean.strip()}")

    client.close()
    print("Done!")


if __name__ == "__main__":
    deploy()
