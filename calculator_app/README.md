# Calculator Web Application

A simple web-based calculator built with **Python, FastAPI, Pydantic, HTML, CSS, and JavaScript**.

This project was developed to practice Python programming, REST API development, request validation, automated testing, and Git workflows.

The application provides a REST API for mathematical operations and a browser-based user interface.

## Features

- Addition, subtraction, multiplication, and division
- REST API built with FastAPI
- Request and response validation using Pydantic
- Error handling for invalid requests and division by zero
- Responsive web interface using HTML, CSS, and JavaScript
- Optional local frontend hosting through FastAPI
- Automated tests using pytest
- Interactive API documentation using Swagger UI

## Technologies

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API framework |
| Pydantic | Data validation |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | API requests and user interaction |
| pytest | Automated testing |
| Git & GitHub | Version control |

## Project Structure

```text
calculator_app/
├── api/
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── gui/
├── input/
├── operations/
│   └── math_functions.py
├── tests/
│   ├── test_api.py
│   └── test_collection.py
├── main.py
└── requirements.txt
```

The `operations` directory contains reusable mathematical functions shared by the API and the original command-line application.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/valtteri-cybersecurity/school-projects.git
cd school-projects/calculator_app
```

### 2. Create a virtual environment

From the `calculator_app` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Start the API and frontend

```bash
SERVE_FRONTEND=true python -m uvicorn api.main:app --reload
```

Open the calculator in your browser:

**http://127.0.0.1:8000/ui/**

### Start the API without the frontend

```bash
python -m uvicorn api.main:app --reload
```

By default, static frontend hosting is disabled.

This configuration allows the backend to run independently from the frontend, supporting future cloud deployment.

## API Documentation

FastAPI automatically generates interactive API documentation.

**Swagger UI:**

http://127.0.0.1:8000/docs

### Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API availability |
| POST | `/calculate` | Perform a mathematical operation |

### Example API Request

**POST `/calculate`**

```json
{
  "a": 100,
  "b": 20,
  "operation": "divide"
}
```

**Response:**

```json
{
  "result": 5.0
}
```

### Supported Operations

| Operation | Description |
|---|---|
| `add` | Addition |
| `subtract` | Subtraction |
| `multiply` | Multiplication |
| `divide` | Division |

### Error Handling

The API uses standard HTTP status codes:

- **200 OK:** Successful calculation
- **400 Bad Request:** Division by zero
- **422 Unprocessable Content:** Invalid request data or unsupported operation

Pydantic validates incoming requests before calculations are performed.

## Automated Testing

The project uses **pytest** for automated testing.

Run all calculator tests from the `calculator_app` directory:

```bash
python -m pytest tests/ -v
```

Latest verified test results:

```text
38 passed, 1 warning
```

Tests cover mathematical operations, command-line functionality, and API behavior.

## Development Workflow

Development follows a Git feature-branch workflow:

1. Create a GitHub issue.
2. Create a feature branch.
3. Implement the changes.
4. Write and execute automated tests.
5. Commit and push the changes.
6. Open a pull request targeting the `Development` branch.
7. Review and merge the pull request.

## Future Improvements

- Expand API validation and error-handling tests
- Add additional mathematical operations
- Deploy the FastAPI backend using AWS Lambda and API Gateway
- Host the frontend using Amazon S3 and CloudFront
- Implement CI/CD using GitHub Actions

## Project Status

**Development — Local web application functional**

The calculator API and browser interface have been implemented and tested locally. AWS deployment is planned for a future development phase.
