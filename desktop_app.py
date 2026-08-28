import os
import sys
import time
import threading
import socket
from pathlib import Path

import django
import webview
from django.core.management import call_command


# ============================================================
# APPLICATION PATH
# ============================================================

if getattr(sys, "frozen", False):
    # Running as a PyInstaller EXE
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Running normally with Python
    BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# DJANGO PATH
# ============================================================

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)


# ============================================================
# INITIALIZE DJANGO
# ============================================================

django.setup()


# ============================================================
# CHECK WHETHER DJANGO IS RUNNING
# ============================================================

def server_is_running(
    host="127.0.0.1",
    port=8000,
):
    """
    Check whether the Django server is listening.
    """

    try:
        with socket.create_connection(
            (host, port),
            timeout=0.5,
        ):
            return True

    except OSError:
        return False


# ============================================================
# START DJANGO
# ============================================================

def start_django():
    """
    Start Django in the background.
    """

    try:

        if server_is_running():

            print(
                "Django is already running."
            )

            return

        call_command(
            "runserver",
            "127.0.0.1:8000",
            "--noreload",
        )

    except Exception as error:

        print(
            "Django server error:"
        )

        print(error)


# ============================================================
# WAIT FOR DJANGO
# ============================================================

def wait_for_django(
    timeout=30,
):
    """
    Wait until Django is ready.
    """

    start_time = time.time()

    while (
        time.time() - start_time
        < timeout
    ):

        if server_is_running():

            return True

        time.sleep(0.25)

    return False


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    print(
        "=========================================="
    )

    print(
        "       ISC POOL TRACKER"
    )

    print(
        "=========================================="
    )

    print(
        f"Application directory: {BASE_DIR}"
    )

    print(
        "Starting Django..."
    )


    # --------------------------------------------------------
    # START DJANGO
    # --------------------------------------------------------

    django_thread = threading.Thread(
        target=start_django,
        daemon=True,
    )

    django_thread.start()


    # --------------------------------------------------------
    # WAIT FOR DJANGO
    # --------------------------------------------------------

    if not wait_for_django():

        print(
            "ERROR: Django failed to start."
        )

        return


    print(
        "Django server is ready."
    )


    # --------------------------------------------------------
    # CREATE DESKTOP WINDOW
    # --------------------------------------------------------

    webview.create_window(

        "ISC Pool Tracker",

        "http://127.0.0.1:8000/",

        width=1400,

        height=900,

        min_size=(
            900,
            600,
        ),

        resizable=True,

        text_select=True,

    )


    # --------------------------------------------------------
    # START PYWEBVIEW
    # --------------------------------------------------------

    webview.start(
        debug=False,
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()