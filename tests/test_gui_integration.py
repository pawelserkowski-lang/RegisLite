import pytest
from playwright.sync_api import Page, expect
import threading
import uvicorn
import time
import re
import asyncio
from src.main import app

# Start server in a separate thread
# We use a different port to avoid conflicts with other tests or running services
PORT = 8003

class ServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.should_exit = False
        self.daemon = True

    def run(self):
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        config = uvicorn.Config(self.app, host="127.0.0.1", port=PORT, loop="asyncio")
        server = uvicorn.Server(config)

        # Override install_signal_handlers to do nothing (not needed in thread)
        server.install_signal_handlers = lambda: None

        # Run server using loop.run_until_complete instead of asyncio.run
        # This avoids conflict if nest_asyncio was applied globally (though we removed it)
        # And gives us more control.
        try:
            loop.run_until_complete(server.serve())
        finally:
            loop.close()

@pytest.fixture(scope="module", autouse=True)
def server():
    # Start server in thread
    t = ServerThread(app)
    t.start()

    # Wait for server to accept connections
    timeout = 10
    start = time.time()
    connected = False
    import socket
    while time.time() - start < timeout:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', PORT))
        sock.close()
        if result == 0:
            connected = True
            break
        time.sleep(0.1)

    if not connected:
        raise RuntimeError("Server failed to start")

    yield
    # No easy clean shutdown for daemon thread, it dies with process

def test_gui_auto_fix_flow(page: Page, tmp_path):
    """
    Test that uploading a project and clicking 'Auto-Fix' sends the correct WebSocket command
    and receives a response.
    """
    # Create a dummy zip file
    import zipfile
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr('test.txt', 'hello')

    page.goto(f"http://127.0.0.1:{PORT}/")

    # Upload file
    with page.expect_response("**/upload") as response_info:
        # Check if file input exists, if not wait for it
        page.wait_for_selector('input[type="file"]')
        page.set_input_files('input[type="file"]', str(zip_path))
        page.click('button:text("Upload ZIP")')

    # Wait for upload to complete
    upload_response = response_info.value
    assert upload_response.ok

    expect(page.get_by_text("Auto-Fix")).to_be_enabled()

    # Click Auto-Fix
    page.click('button:text("Auto-Fix")')

    # Verify the log message "Uruchamiam Auto-Fixer" appears in the terminal output
    expect(page.locator("#term-output")).to_contain_text("🚀 Uruchamiam Auto-Fixer...")

    # Verify that the status text updates to indicate the process started.
    status_locator = page.locator("#status-text")
    expect(status_locator).to_contain_text(re.compile(r"Autonaprawa|Analizuję|Myślę"))
