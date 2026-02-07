"""Helper script to SSH into the Pi and run diagnostic/fix commands."""
import subprocess
import sys

def run_on_pi(cmd):
    """Run a command on the Pi via SSH using paramiko."""
    try:
        import paramiko
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
        import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("192.168.0.64", username="pi", password="pi", timeout=10)

    # Use sudo with password
    if cmd.startswith("sudo "):
        actual_cmd = f"echo 'pi' | sudo -S {cmd[5:]}"
    else:
        actual_cmd = cmd

    stdin, stdout, stderr = client.exec_command(actual_cmd, timeout=30)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    exit_code = stdout.channel.recv_exit_status()
    client.close()

    result = out
    if err.strip() and "[sudo]" not in err:
        result += f"\nSTDERR: {err}"
    if exit_code != 0:
        result += f"\nEXIT CODE: {exit_code}"
    return result.strip()


if __name__ == "__main__":
    cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hostname && uptime"
    print(run_on_pi(cmd))
