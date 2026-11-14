# Calculator Web Application

A serverless web-based calculator built with **Python, FastAPI, Pydantic, HTML, CSS, JavaScript, and AWS**.

The application was developed as a software development learning project to practice Python programming, REST API development, automated testing, cloud deployment, and Git workflows.

The calculator supports four mathematical operations and provides both a REST API and a responsive browser-based interface.

The application is deployed on AWS using a serverless architecture.

## Features

- Addition, subtraction, multiplication, and division
- REST API built with FastAPI
- Request and response validation using Pydantic
- Error handling for invalid input and division by zero
- Responsive HTML, CSS, and JavaScript frontend
- Original Python command-line calculator
- Automated unit and API testing with pytest
- Continuous integration using GitHub Actions
- AWS Lambda backend with Mangum
- Amazon API Gateway HTTP API
- Static frontend hosting using Amazon S3
- HTTPS delivery through Amazon CloudFront
- CORS configuration for frontend-to-API communication
- Interactive API documentation using Swagger UI

## Technologies

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend programming |
| FastAPI | REST API framework |
| Pydantic | Request and response validation |
| Mangum | AWS Lambda ASGI adapter |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | API requests and user interaction |
| pytest | Automated testing |
| Git & GitHub | Version control |
| GitHub Actions | Continuous integration |
| AWS Lambda | Serverless backend execution |
| Amazon API Gateway | Public HTTPS API |
| Amazon S3 | Frontend file storage |
| Amazon CloudFront | CDN and HTTPS frontend delivery |
| Amazon CloudWatch | Lambda execution logs |

## Project Structure

```text
school-projects/
├── .github/
│   └── workflows/
│       └── calculator-pytest.yml
│
└── calculator_app/
    ├── api/
    │   ├── config.py
    │   ├── main.py
    │   ├── schemas.py
    │   └── lambda_handler.py
    │
    ├── frontend/
    │   ├── index.html
    │   ├── style.css
    │   └── app.js
    │
    ├── gui/
    │   └── menu.py
    │
    ├── input/
    │   ├── messages.py
    │   └── user_input.py
    │
    ├── operations/
    │   └── math_functions.py
    │
    ├── tests/
    │   ├── test_api.py
    │   └── test_collection.py
    │
    ├── main.py
    ├── requirements.txt
    └── README.md
```

The `operations` directory contains reusable mathematical functions shared by the command-line application and the FastAPI backend.

The `api/lambda_handler.py` module provides the AWS Lambda entry point using Mangum.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/valtteri-cybersecurity/school-projects.git
cd school-projects/calculator_app
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

The dependencies include FastAPI, Uvicorn, HTTPX, pytest, and Mangum.

## Running the Application Locally

### Start the FastAPI Backend

From the `calculator_app` directory:

```bash
python -m uvicorn api.main:app --reload
```

The API is available at:

http://127.0.0.1:8000

### Start the API with Local Frontend Hosting

```bash
SERVE_FRONTEND=true python -m uvicorn api.main:app --reload
```

Open:

http://127.0.0.1:8000/ui/

**Note:** The frontend JavaScript is currently configured to call the deployed AWS API. To use the local FastAPI backend instead, change `API_BASE_URL` in `frontend/app.js` to an empty string before serving the frontend locally.

### Run the Original CLI Calculator

```bash
python main.py
```

## REST API

The backend exposes two primary endpoints.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API availability |
| POST | `/calculate` | Perform a mathematical calculation |

### API Health Check

Request:

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Perform a Calculation

Request:

```http
POST /calculate
Content-Type: application/json
```

Request body:

```json
{
  "a": 100,
  "b": 25,
  "operation": "divide"
}
```

Response:

```json
{
  "result": 4.0
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

The API uses standard HTTP status codes.

- **200 OK:** Successful calculation
- **400 Bad Request:** Division by zero
- **422 Unprocessable Content:** Invalid request data or unsupported operation

Pydantic validates incoming requests before mathematical operations are performed.

The API rejects unexpected request fields and unsupported operation names.

### Interactive API Documentation

FastAPI automatically generates interactive API documentation.

When running locally:

http://127.0.0.1:8000/docs

## AWS Serverless Architecture

The application is deployed using managed AWS services.

### Frontend

**Amazon S3**

Stores the static website files:

- `index.html`
- `style.css`
- `app.js`

The S3 bucket remains private.

**Amazon CloudFront**

Delivers the frontend over HTTPS using the CloudFront distribution domain.

CloudFront accesses the private S3 bucket using Origin Access Control (OAC).

### Backend

**Amazon API Gateway**

Provides the public HTTPS API endpoints and forwards requests to AWS Lambda.

**AWS Lambda**

Executes the Python FastAPI application without requiring a continuously running application server.

**Mangum**

Acts as an ASGI adapter between AWS Lambda events and FastAPI.

**Amazon CloudWatch**

Collects Lambda execution logs for troubleshooting and monitoring.

### Request Flow

```text
User Browser
     |
     v
Amazon CloudFront
     |
     v
Amazon S3
     |
     v
HTML + CSS + JavaScript
     |
     | HTTPS API Request
     v
Amazon API Gateway
     |
     v
AWS Lambda
     |
     v
Mangum
     |
     v
FastAPI
     |
     v
Python Math Functions
     |
     v
JSON Response
     |
     v
User Browser
```

The frontend and backend are deployed independently.

## AWS Deployment Configuration

| Component | Configuration |
|---|---|
| AWS Region | eu-north-1 (Europe/Stockholm) |
| Lambda function | `calculator-api` |
| Lambda runtime | Python 3.12 |
| Lambda architecture | x86_64 |
| Lambda handler | `api.lambda_handler.handler` |
| API Gateway | HTTP API |
| API Gateway name | `calculator-http-api` |
| S3 bucket | `calculator-frontend-418` |
| CloudFront distribution | `calculator-frontend` |

### Public API

The deployed API is available at:

https://tqlc3bk5s0.execute-api.eu-north-1.amazonaws.com

Health endpoint:

https://tqlc3bk5s0.execute-api.eu-north-1.amazonaws.com/health

### Frontend API Configuration

The frontend connects to the deployed API using the following JavaScript configuration:

```javascript
const API_BASE_URL = "https://tqlc3bk5s0.execute-api.eu-north-1.amazonaws.com";
```

The frontend sends calculation requests using the Fetch API.

### CORS Configuration

API Gateway is configured to allow browser requests from the CloudFront frontend origin.

The configuration permits the required HTTP methods and the `Content-Type` request header.

The allowed origin should match the deployed CloudFront HTTPS domain.

## AWS Lambda Deployment

The FastAPI application uses Mangum to support AWS Lambda execution.

### Lambda Handler

File: `api/lambda_handler.py`

```python
from mangum import Mangum
from api.main import app


handler = Mangum(app, lifespan="off")
```

The Lambda handler configuration is:

```text
api.lambda_handler.handler
```

### Deployment Package

The Lambda deployment package contains the application source code and production dependencies.

```text
calculator-lambda.zip
├── api/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   └── lambda_handler.py
├── operations/
│   └── math_functions.py
├── fastapi/
├── mangum/
└── other dependencies
```

The application directories and Python dependencies must be placed at the root of the ZIP archive.

### Deployment Method

The current deployment process is manual.

Backend deployment:

1. Build the Lambda deployment package.
2. Include the required production dependencies.
3. Upload the ZIP file to AWS Lambda.
4. Verify the Lambda handler configuration.
5. Test the Lambda function.
6. Verify API Gateway endpoints.

Frontend deployment:

1. Update the frontend files.
2. Upload the updated files to Amazon S3.
3. Invalidate the relevant CloudFront cache paths when necessary.
4. Verify the deployed website.

Automated deployment through GitHub Actions CD is planned.

## Automated Testing

The project uses pytest to test mathematical operations, command-line functionality, and API endpoints.

### Run Tests Locally

From the `calculator_app` directory:

```bash
python -m pytest tests/ -v
```

The previously verified test suite contained 38 passing tests.

### Test Coverage Areas

- Addition
- Subtraction
- Multiplication
- Division
- Division by zero
- User input validation
- Command-line menu navigation
- Application output
- FastAPI health endpoint
- API calculation endpoints
- Invalid API operations

## Continuous Integration

The project uses GitHub Actions to automatically execute pytest tests.

Workflow file:

```text
.github/workflows/calculator-pytest.yml
```

### CI Workflow

The workflow:

1. Checks out the GitHub repository.
2. Sets up Python 3.12.
3. Installs dependencies from `requirements.txt`.
4. Runs the calculator pytest test suite.
5. Reports the test results in GitHub Actions.

### Workflow Triggers

The workflow runs when relevant files change in:

- Pushes to `main`
- Pushes to `feature/**` branches
- Pull requests affecting the calculator

Manual execution is also supported.

### CI Security

The workflow uses read-only repository permissions:

```yaml
permissions:
  contents: read
```

AWS deployment credentials are not required for the current CI workflow.

Continuous deployment is not yet implemented.

## Development Workflow

The project follows a Git feature-branch workflow.

1. Create a GitHub issue describing the change.
2. Create a feature branch from `main`.
3. Implement the feature or fix.
4. Write or update relevant tests.
5. Run pytest locally.
6. Commit and push the changes.
7. Open a pull request targeting `main`.
8. Verify the GitHub Actions CI result.
9. Review and merge the pull request.

The `main` branch contains the stable project version.

## Security Considerations

The application uses several security measures:

- Input validation with Pydantic
- Explicitly supported mathematical operations
- Error handling for invalid requests
- HTTPS communication through CloudFront and API Gateway
- Private S3 bucket
- CloudFront Origin Access Control
- Restricted cross-origin browser access
- AWS Lambda execution role with limited permissions
- Automated tests before merging code changes

The API is publicly accessible. CORS controls browser access but is not an authentication mechanism.

Additional protections, including API throttling, cost monitoring, and security reviews, are planned.

## Future Improvements

### CI/CD Automation

- Implement GitHub Actions continuous deployment
- Configure AWS authentication using GitHub OIDC
- Automate Lambda deployment package creation
- Automate Lambda code updates
- Automate S3 frontend deployment
- Automate CloudFront cache invalidation
- Require successful CI checks before production deployment

### Security and Reliability

- Review IAM least-privilege permissions
- Configure API Gateway throttling
- Configure AWS budget alerts
- Improve application monitoring
- Expand API validation and error-handling tests
- Add automated deployment verification

### Application Development

- Improve the frontend user experience
- Add additional mathematical operations
- Expand automated tests
- Improve project documentation

## Project Status

**Operational — Deployed on AWS**

The calculator has been successfully deployed as a serverless web application.

The following components have been implemented and tested:

- Python calculator
- FastAPI backend
- Pydantic request validation
- Browser-based frontend
- Automated pytest testing
- GitHub Actions CI
- AWS Lambda
- Amazon API Gateway
- Amazon S3
- Amazon CloudFront
- HTTPS communication between frontend and backend

The deployed application successfully performs calculations through the browser.

**Current deployment:** Manual

**Next milestone:** Automated deployment using GitHub Actions CD and AWS OIDC authentication.

---

## Author

Developed as part of Python programming, software development, REST API, automated testing, and AWS cloud computing studies.

**GitHub:** [valtteri-cybersecurity](https://github.com/valtteri-cybersecurity)

**Repository:** [school-projects](https://github.com/valtteri-cybersecurity/school-projects)
