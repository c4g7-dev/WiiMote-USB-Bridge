"""Deploy wiimote_bridge.py to the Pi and restart the service."""
import paramiko
import sys

PI_HOST = "192.168.0.64"
PI_USER = "pi"
PI_PASS = "pi"
REMOTE_PATH = "/opt/wiimote-bridge/wiimote_bridge.py"
LOCAL_PATH = "wiimote_bridge.py"


def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(PI_HOST, username=PI_USER, password=PI_PASS, timeout=10)

    # Upload via SFTP to /tmp first (writable by pi user)
    print("Uploading wiimote_bridge.py ...")
    sftp = client.open_sftp()
    sftp.put(LOCAL_PATH, "/tmp/wiimote_bridge.py")
    sftp.close()
    print("Upload complete.")

    # Copy to install dir and restart service
    commands = [
        "sudo cp /tmp/wiimote_bridge.py /opt/wiimote-bridge/wiimote_bridge.py",
        "sudo systemctl restart wiimote-bridge",
    ]
    for cmd in commands:
        full_cmd = f"echo '{PI_PASS}' | sudo -S {cmd.replace('sudo ', '', 1)}"
        print(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(full_cmd, timeout=30)
        out = stdout.read().decode()
        err = stderr.read().decode()
        rc = stdout.channel.recv_exit_status()
        if out.strip():
            print(f"  stdout: {out.strip()}")
        if rc != 0:
            # Filter out sudo password prompt noise
            err_clean = "\n".join(
                l for l in err.splitlines() if "[sudo]" not in l
            )
            if err_clean.strip():
                print(f"  stderr: {err_clean.strip()}")
            print(f"  exit code: {rc}")

    client.close()
    print("Done! Service restarted.")


if __name__ == "__main__":
    deploy()
