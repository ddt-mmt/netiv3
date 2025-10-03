# netiV3 - AI-Powered Network Analysis Tool

## Installation

To set up and run the netiV3 application, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```
    (Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY_NAME` with your actual GitHub details.)

2.  **Create a Python Virtual Environment:**
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    ```bash
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    Install all required Python packages.
    ```bash
    pip install -r netiV3/requirements.txt
    ```

5.  **Set Environment Variables:**
    The application requires a `SECRET_KEY` and optionally a `GEMINI_API_KEY`.
    ```bash
    export SECRET_KEY="your_secret_key_here"
    export GEMINI_API_KEY="your_gemini_api_key_here" # Optional, for AI analysis
    ```
    (Replace `"your_secret_key_here"` and `"your_gemini_api_key_here"` with your actual keys.)

6.  **Run the Application:**
    ```bash
    gunicorn -w 4 run:app -b 0.0.0.0:5004
    ```
    The application should now be running on `http://0.0.0.0:5004`.

## Usage

(Further usage instructions can be added here later.)