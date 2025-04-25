# Python Online Compiler

A web-based Python compiler that allows users to write and execute Python code directly in the browser. This project is perfect for educational purposes and quick Python code testing.

## Features

- Modern, user-friendly interface
- Real-time code editing with syntax highlighting
- Python code execution with output display
- Error handling and timeout protection
- Responsive design that works on all devices

## Prerequisites

- Python 3.x
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Security Notes

- The application runs Python code in a controlled environment
- Execution timeout is set to 10 seconds to prevent infinite loops
- File system access is limited for security

## Technologies Used

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Code Editor: CodeMirror
- Styling: Bootstrap 5
- Icons: Font Awesome

## Contributing

Feel free to submit issues and enhancement requests! 