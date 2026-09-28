import os
import socket
import subprocess
import time

import requests

API_URL = "http://localhost:8000"
UI_URL = "http://localhost:8502"
UI_PORT = 8502

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

CHROME_PATH = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)


def is_port_available(port):
    """Return True when the requested port is available."""
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:
        sock.settimeout(1)
        return (
            sock.connect_ex(
                ("localhost", port)
            )
            != 0
        )


def is_service_running(url):
    """Check whether an HTTP service is responding."""
    try:
        response = requests.get(
            url,
            timeout=2,
        )
        return response.ok
    except requests.RequestException:
        return False


def start_docker():
    """Start the existing Docker image without rebuilding."""
    print(
        "🚀 Starting Company Policy Agent backend..."
    )

    subprocess.run(
        [
            "docker",
            "compose",
            "up",
            "-d",
        ],
        check=True,
    )


def wait_for_api():
    """Wait until the FastAPI backend becomes healthy."""
    print(
        "⏳ Waiting for API to become ready..."
    )

    for attempt in range(90):
        try:
            response = requests.get(
                f"{API_URL}/health",
                timeout=3,
            )

            if response.ok:
                data = response.json()

                if data.get("status") in (
                    "healthy",
                    "ok",
                ):
                    print(
                        "✅ API is healthy."
                    )
                    return

        except requests.RequestException:
            pass

        print(
            f"   Waiting... ({attempt + 1}/90)"
        )

        time.sleep(2)

    raise RuntimeError(
        "❌ FastAPI did not become healthy "
        "within the expected time."
    )


def start_ui():
    """Start the unified Streamlit application."""
    if not is_port_available(UI_PORT):
        raise RuntimeError(
            f"❌ Port {UI_PORT} is already in use."
        )

    print(
        "🖥️ Starting Company Policy Agent UI..."
    )

    environment = os.environ.copy()

    existing_pythonpath = environment.get(
        "PYTHONPATH",
        "",
    )

    if existing_pythonpath:
        environment["PYTHONPATH"] = (
            PROJECT_ROOT
            + os.pathsep
            + existing_pythonpath
        )
    else:
        environment["PYTHONPATH"] = (
            PROJECT_ROOT
        )

    print(
        f"   Python path: {PROJECT_ROOT}"
    )

    process = subprocess.Popen(
        [
            "streamlit",
            "run",
            "app/ui.py",
            "--server.port",
            str(UI_PORT),
            "--server.headless",
            "true",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
    )

    return process


def wait_for_ui():
    """Wait until the unified Streamlit UI responds."""
    print(
        "⏳ Waiting for Streamlit UI..."
    )

    for attempt in range(30):
        if is_service_running(UI_URL):
            print(
                "✅ Streamlit UI is running."
            )
            return

        print(
            f"   Waiting... ({attempt + 1}/30)"
        )

        time.sleep(1)

    raise RuntimeError(
        "❌ Streamlit UI did not start."
    )


def open_chrome():
    """Open the unified application in Chrome."""
    print(
        "🌐 Opening Company Policy Agent..."
    )

    try:
        subprocess.Popen(
            [
                CHROME_PATH,
                UI_URL,
            ]
        )

    except FileNotFoundError:
        print(
            "⚠️ Chrome was not found at:"
        )
        print(
            f"   {CHROME_PATH}"
        )
        print()
        print(
            "Open this URL manually:"
        )
        print(
            f"   🤖 Company Policy Agent: {UI_URL}"
        )


def main():
    ui_process = None

    try:
        start_docker()
        wait_for_api()

        ui_process = start_ui()
        wait_for_ui()

        open_chrome()

        print()
        print("=" * 60)
        print(
            "🚀 Company Policy Agent Started"
        )
        print("=" * 60)
        print()

        print(
            "🤖 Unified Streamlit Application:"
        )
        print(
            f"   {UI_URL}"
        )
        print()

        print(
            "📊 Monitoring Dashboard:"
        )
        print(
            "   Open the Streamlit sidebar "
            "and select Monitoring Dashboard."
        )
        print()

        print(
            "⚡ FastAPI:"
        )
        print(
            f"   {API_URL}"
        )
        print()

        print(
            "Press Ctrl+C to stop applications "
            "started by this script."
        )
        print("=" * 60)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(
            "\n🛑 Stopping applications "
            "started by this script..."
        )

    finally:
        if ui_process is not None:
            ui_process.terminate()

            try:
                ui_process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:
                ui_process.kill()

        print(
            "🛑 Stopping Docker services..."
        )

        subprocess.run(
            [
                "docker",
                "compose",
                "down",
            ],
            check=False,
        )

        print(
            "✅ Everything stopped."
        )


if __name__ == "__main__":
    main()