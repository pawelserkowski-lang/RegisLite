import pytest
from playwright.sync_api import Page, expect
import threading
import uvicorn
import time
import re
import os
from src.main import app

# Start server in a separate thread
# We use a different port to avoid conflicts with other tests or running services
PORT = 8003

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=PORT)

@pytest.fixture(scope="module", autouse=True)
def server():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2) # Wait for server to start
    yield
    # No easy way to stop uvicorn in thread, but daemon will kill it on exit

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
    # It might transition quickly from "Autonaprawa..." (frontend) to "Analizuję..." (backend response).
    status_locator = page.locator("#status-text")
    expect(status_locator).to_contain_text(re.compile(r"Autonaprawa|Analizuję|Myślę"))
