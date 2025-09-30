# Project Setup Guide

This guide will help you set up a Python virtual environment, activate it, install the required dependencies using `requirements.txt`, and run your development server.

## 1. Create a Virtual Environment

Open your terminal and navigate to the project directory. Then, run the following command to create a new virtual environment named `venv`:

```bash
uv venv
```

## 2. Activate the Virtual Environment

- **On Linux or macOS:**

    ```bash
    source venv/bin/activate
    ```

- **On Windows:**

    ```cmd
    .venv\Scripts\activate
    ```

## 3. Install the Requirements

After activating the virtual environment, install the required dependencies:

```bash
cd <repoName>
uv pip install -r requirements.txt
```

## 4. Run the Development Server

To start your application’s development server, use the following command (commonly used for Django or Flask projects):

- **For Django:**

    ```bash
    python manage.py runserver
    ```

## 5. You're All Set!

Now you can run or develop your project in your isolated environment.

---

**Note:**  
If you ever want to deactivate the virtual environment, simply run:

```bash
deactivate
```
