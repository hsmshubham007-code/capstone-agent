import socket
import subprocess
import sys
import time

import requests

API_URL = "http://localhost:8000"
MONITORING_URL = "http://localhost:8501"
UI_URL = "http://localhost:8502"

MONITORING_PORT = 8501
UI_PORT = 8502

CHROME_PATH = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)


def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)

        return sock.connect_ex(
            ("localhost", port)
        ) != 0


def is_service_running(url):
    try:
        response = requests.get(
            url,
            timeout=2,
        )

        return response.ok

    except requests.RequestException:
        return False


def start_docker():
    print("🐳 Starting Company Policy Agent backend...")

    subprocess.run(
        ["docker", "compose", "up", "-d"],
        check=True,
    )


def wait_for_api():
    print("⏳ Waiting for API to become ready...")

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
                    print("✅ API is healthy.")
                    return

        except requests.RequestException:
            pass

        print(
            f"   Waiting... ({attempt + 1}/90)"
        )

        time.sleep(2)

    raise RuntimeError(
        "❌ API did not become healthy "
        "within 180 seconds."
    )


def start_monitoring():
    if not is_port_available(MONITORING_PORT):

        if is_service_running(MONITORING_URL):
            print(
                "📊 Monitoring Dashboard "
                "is already running."
            )

            return None

        raise RuntimeError(
            f"❌ Port {MONITORING_PORT} "
            "is already in use."
        )

    print(
        "📊 Starting Monitoring Dashboard..."
    )

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "monitoring_dashboard.py",
            "--server.port",
            str(MONITORING_PORT),
            "--server.headless",
            "true",
        ]
    )


def wait_for_monitoring():
    print(
        "⏳ Waiting for Monitoring Dashboard..."
    )

    for attempt in range(30):

        if is_service_running(
            MONITORING_URL
        ):
            print(
                "✅ Monitoring Dashboard "
                "is running."
            )

            return

        time.sleep(1)

    raise RuntimeError(
        "❌ Monitoring Dashboard "
        "did not start."
    )


def start_ui():
    if not is_port_available(UI_PORT):
        if is_service_running(UI_URL):
            print(
                "🤖 Company Policy UI "
                "is already running."
            )
            return None

        raise RuntimeError(
            f"❌ Port {UI_PORT} "
            "is already in use."
        )

    print(
        "🤖 Starting Company Policy UI..."
    )

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/ui.py",
            "--server.port",
            str(UI_PORT),
            "--server.headless",
            "true",
        ]
    )


def open_chrome():
    print("🌐 Opening Company Policy Agent in Chrome...")

    try:
        subprocess.Popen(
            [
                CHROME_PATH,
                MONITORING_URL,
                UI_URL,
            ]
        )

        print(
            "✅ Chrome opened with Monitoring "
            "Dashboard and Company Policy UI."
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
            "Open these URLs manually:"
        )

        print(
            f"   📊 Monitoring: {MONITORING_URL}"
        )

        print(
            f"   🤖 Company Policy UI: {UI_URL}"
        )


def main():
    monitoring_process = None
    ui_process = None

    try:
        # --------------------------------------------------
        # 1. Start backend
        # --------------------------------------------------

        start_docker()

        wait_for_api()

        # --------------------------------------------------
        # 2. Start/check monitoring dashboard
        # --------------------------------------------------

        monitoring_process = start_monitoring()

        wait_for_monitoring()

        # --------------------------------------------------
        # 3. Start/check Company Policy UI
        # --------------------------------------------------

        ui_process = start_ui()

        # Give Streamlit a moment to finish initializing.
        time.sleep(2)

        # --------------------------------------------------
        # 4. Open both applications in Chrome
        # --------------------------------------------------

        open_chrome()

        # --------------------------------------------------
        # 5. Display startup information
        # --------------------------------------------------

        print()
        print("=" * 60)
        print("🚀 Company Policy Agent Started")
        print("=" * 60)
        print()

        print("📊 Monitoring Dashboard:")
        print(
            f"   {MONITORING_URL}"
        )

        print()

        print("🤖 Company Policy UI:")
        print(
            f"   {UI_URL}"
        )

        print()

        print("🐳 FastAPI:")
        print(
            f"   {API_URL}"
        )

        print()

        print(
            "Press Ctrl+C to stop applications "
            "started by this script."
        )

        print("=" * 60)

        # --------------------------------------------------
        # Keep script running
        # --------------------------------------------------

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(
            "\n🛑 Stopping applications "
            "started by this script..."
        )

    finally:
        # Only terminate Streamlit processes
        # that THIS script started.

        if ui_process is not None:
            ui_process.terminate()

        if monitoring_process is not None:
            monitoring_process.terminate()

        print(
            "🐳 Stopping Docker services..."
        )

        subprocess.run(
            ["docker", "compose", "down"],
            check=False,
        )

        print(
            "✅ Everything stopped."
        )


if __name__ == "__main__":
    main()