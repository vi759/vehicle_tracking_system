import os
import subprocess
import sys


def kill_port_windows(port):
    """Kill processes on a port — Windows implementation."""
    print(f"Attempting to kill processes on port {port}...")
    try:
        cmd = f"netstat -ano | findstr :{port}"
        output = subprocess.check_output(cmd, shell=True).decode()

        pids = set()
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                pids.add(pid)

        if not pids:
            print(f"No processes found on port {port}.")
            return

        for pid in pids:
            if pid == "0":
                continue
            print(f"Killing PID {pid}...")
            os.system(f"taskkill /F /PID {pid}")

        print("Cleanup complete. You can now run the app.")

    except subprocess.CalledProcessError:
        print(f"No processes found on port {port}.")
    except Exception as e:
        print(f"Error: {e}")


def kill_port_unix(port):
    """Kill processes on a port — Linux/macOS implementation."""
    print(f"Attempting to kill processes on port {port}...")
    try:
        # lsof lists open files/ports; -t returns PIDs only
        result = subprocess.check_output(
            ["lsof", "-ti", f"tcp:{port}"]
        ).decode().strip()

        if not result:
            print(f"No processes found on port {port}.")
            return

        pids = result.splitlines()
        for pid in pids:
            pid = pid.strip()
            if pid:
                print(f"Killing PID {pid}...")
                os.kill(int(pid), 9)

        print("Cleanup complete. You can now run the app.")

    except subprocess.CalledProcessError:
        print(f"No processes found on port {port}.")
    except FileNotFoundError:
        # lsof not available; try fuser
        try:
            subprocess.run(["fuser", "-k", f"{port}/tcp"], check=True)
            print("Cleanup complete.")
        except Exception as e:
            print(f"Could not kill port {port}: {e}")
    except Exception as e:
        print(f"Error: {e}")


def kill_port(port):
    # FIX: Added cross-platform support (previously Windows-only)
    if sys.platform == "win32":
        kill_port_windows(port)
    else:
        kill_port_unix(port)


if __name__ == "__main__":
    kill_port(5000)
