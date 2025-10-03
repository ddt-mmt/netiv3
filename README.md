# netiV3 Project Rollback Instructions

This document provides instructions on how to roll back the `netiV3` application to a previous working state using a backup archive.

## Backup Archive

The latest backup archive is located at: `/usr/lib/gemini-cli/netiV3_backup_latest.tar.gz`

## Rollback Procedure

Follow these steps to perform a rollback:

1.  **Stop the netiV3 service:**
    ```bash
    sudo systemctl stop netiV3
    ```

2.  **Remove the current netiV3 application directory:**
    ```bash
    sudo rm -rf /usr/lib/gemini-cli/netiV3
    ```

3.  **Extract the backup archive:**
    This command will extract the contents of the backup directly into the correct location, preserving the directory structure.
    ```bash
    sudo tar -xzf /usr/lib/gemini-cli/netiV3_backup_latest.tar.gz -C /
    ```

4.  **Recreate the Python virtual environment:**
    It's crucial to recreate the virtual environment to ensure all dependencies are correctly linked and up-to-date.
    ```bash
    python3 -m venv /usr/lib/gemini-cli/netiV3/venv
    ```

5.  **Install application dependencies:**
    Install all required Python packages from the `requirements.txt` file.
    ```bash
    /usr/lib/gemini-cli/netiV3/venv/bin/pip install -r /usr/lib/gemini-cli/netiV3/requirements.txt
    ```

6.  **Reload the systemd daemon:**
    This ensures systemd recognizes any changes to service configurations.
    ```bash
    sudo systemctl daemon-reload
    ```

7.  **Start the netiV3 service:**
    ```bash
    sudo systemctl start netiV3
    ```

8.  **Verify the service status:**
    Check if the service is running correctly.
    ```bash
    sudo systemctl status netiV3
    ```
    You should see `Active: active (running)`.

## Important Notes

*   **API Key for AI Analysis:** The Gemini AI analysis feature requires a `GEMINI_API_KEY`. Ensure this is provided securely at runtime (e.g., via environment variables) as it is not stored in service files.
*   **NSLookup Behavior:** When using NSLookup, providing an IP address will perform a reverse DNS lookup. For forward DNS lookup, provide a domain name.

This concludes the rollback instructions.