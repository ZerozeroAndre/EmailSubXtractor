# EmailSubXtractor

EmailSubXtractor is a full-stack application that processes email data to extract subscription information using a GPT-based backend and presents the results with an interactive React frontend. The project cleans email HTML content, extracts structured subscription data (such as subscription name, cost, cycle, etc.), and provides analytical insights.

## Features

- **Email Cleaning:**  
  Strips unwanted HTML tags and invisible characters from email bodies.
  
- **Subscription Data Extraction:**  
  Uses the OpenAI GPT API to extract structured subscription information from emails.
  
- **Analytics Dashboard:**  
  Displays metrics such as the total number of emails processed, average email body length, and count of emails with subscription info.
  
- **File Upload:**  
  Allows users to upload a JSON file containing a list of email objects for processing.
  
- **Full-Stack Integration:**  
  Seamlessly integrates a FastAPI backend with a React frontend.

## Tech Stack

- **Backend:**
  - Python 3
  - FastAPI
  - Uvicorn
  - Pydantic
  - BeautifulSoup4
  - OpenAI Python SDK
  - (Optional) python-dotenv for environment variables

- **Frontend:**
  - React (Create React App)
  - Axios

- **Deployment (Optional):**
  - Docker
  - Docker Compose

## Project Structure

```plaintext
EmailSubXtractor/
├── README.md
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env               # (Optional) Environment variables
└── frontend/
    ├── README.md
    ├── package.json
    ├── public/
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── AnalyticsDashboard.jsx
        │   └── EmailList.jsx
        └── services/
            └── api.js
```

## Prerequisites

- **Backend:**
  - Python 3.x installed
  - pip
  - (Optional) Virtual environment tool (e.g., venv)
- **Frontend:**
  - Node.js (v14+ recommended)
  - npm
- **General:**
  - An OpenAI API key (for subscription extraction functionality)

## Setup and Installation

### 1. Backend Setup

#### a. Create and Activate a Virtual Environment

Navigate to the project root and then the backend folder:

```sh
cd backend
python3 -m venv env
source env/bin/activate      # On Windows: .\env\Scripts\activate
```

#### b. Install Dependencies

Ensure you have a requirements.txt file in the backend folder with the following (versions can be adjusted):

```
fastapi
uvicorn
pydantic
beautifulsoup4
openai
python-dotenv
```

Install the dependencies:

```sh
pip install -r requirements.txt
```

#### c. Configure Environment Variables

Create a .env file in the backend folder with your API keys and configuration:

```
OPENAI_API_KEY=your_openai_api_key_here
```

#### d. Run the Backend Server

Start the FastAPI server with Uvicorn:

```sh
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at [http://localhost:8000](http://localhost:8000).

### 2. Frontend Setup

#### a. Navigate to the Frontend Folder

```sh
cd ../frontend
```

#### b. Install npm Dependencies

```sh
npm install
```

#### c. Start the React Development Server

```sh
npm start
```

Your React app will open at [http://localhost:3000](http://localhost:3000).

## Usage

1. **Upload JSON File:**
   On the frontend, use the provided file input to upload a JSON file containing a list of email objects (each object should include keys like subject, body, snippet, and from).
2. **Processing:**
   The backend processes the file via the `/process-emails` endpoint. Each email is cleaned and processed, and GPT is used to extract subscription information.
3. **Analytics:**
   The frontend fetches and displays analytics (via the `/analytics` endpoint) such as total emails processed, average email body length, and the number of emails with extracted subscription info.
4. **View Results:**
   Processed emails, along with the extracted subscription details, are displayed on the frontend for review.

## Docker Deployment (Optional)

You can containerize the entire project using Docker and Docker Compose.

### a. Backend Dockerfile

Create a Dockerfile in the backend folder:

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### b. Frontend Dockerfile

Create a Dockerfile in the frontend folder:

```Dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
```

### c. Docker Compose Configuration

In the project root, create a `docker-compose.yml` file:

```yaml
version: "3.8"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

Start both services:

```sh
docker-compose up --build
```

The backend will be available on port 8000 and the frontend on port 3000.

### d. Create a .env File

Create a .env file in the root directory of your project with the OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Project with Docker

To run the entire project using Docker, follow these steps:

1. **Ensure Docker is installed:**
   Make sure Docker is installed and running on your machine. You can download Docker from [here](https://www.docker.com/products/docker-desktop).

2. **Navigate to the project root:**
   Open a terminal and navigate to the root directory of the project where the `docker-compose.yml` file is located.

3. **Build and start the services:**
   Run the following command to build and start the backend and frontend services:

   ```sh
   docker-compose up --build
   ```

   This command will build the Docker images for both the backend and frontend services and start the containers.

4. **Access the services:**
   - The backend API will be available at [http://localhost:8000](http://localhost:8000).
   - The frontend React app will be available at [http://localhost:3000](http://localhost:3000).

5. **Stop the services:**
   To stop the running services, press `Ctrl+C` in the terminal where the `docker-compose` command is running. Alternatively, you can run the following command in a new terminal:

   ```sh
   docker-compose down
   ```

   This command will stop and remove the containers.

## Running the Project without Docker

To run the project without Docker, follow these steps:

### 1. Backend Setup

#### a. Create and Activate a Virtual Environment

Navigate to the project root and then the backend folder:

```sh
cd backend
python3 -m venv env
source env/bin/activate      # On Windows: .\env\Scripts\activate
```

#### b. Install Dependencies

Ensure you have a requirements.txt file in the backend folder with the following (versions can be adjusted):

```
fastapi
uvicorn
pydantic
beautifulsoup4
openai
python-dotenv
```

Install the dependencies:

```sh
pip install -r requirements.txt
```

#### c. Configure Environment Variables

Create a .env file in the backend folder with your API keys and configuration:

```
OPENAI_API_KEY=your_openai_api_key_here
```

#### d. Run the Backend Server

Start the FastAPI server with Uvicorn:

```sh
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at [http://localhost:8000](http://localhost:8000).

### 2. Frontend Setup

#### a. Navigate to the Frontend Folder

```sh
cd ../frontend
```

#### b. Install npm Dependencies

```sh
npm install
```

#### c. Start the React Development Server

```sh
npm start
```

Your React app will open at [http://localhost:3000](http://localhost:3000).

## Usage

1. **Upload JSON File:**
   On the frontend, use the provided file input to upload a JSON file containing a list of email objects (each object should include keys like subject, body, snippet, and from).
2. **Processing:**
   The backend processes the file via the `/process-emails` endpoint. Each email is cleaned and processed, and GPT is used to extract subscription information.
3. **Analytics:**
   The frontend fetches and displays analytics (via the `/analytics` endpoint) such as total emails processed, average email body length, and the number of emails with extracted subscription info.
4. **View Results:**
   Processed emails, along with the extracted subscription details, are displayed on the frontend for review.

## Troubleshooting

- **Backend Errors:**
  Ensure your virtual environment is active and all required packages are installed.
- **Frontend Errors:**
  Check that the API base URL in `src/services/api.js` is correct and that the backend server is running.
- **Environment Variables:**
  Verify that your `.env` file is correctly set up and that `python-dotenv` is loading the variables.
