# "Keep My Job" App

Are you struggling to keep your job? Want to impress your boss and appear marginally more competent?
You are in the right place!

"Keep My Job" is an app that uses an AI multi-agent system to help you to work faster and get more done.

## Demo

Watch this 2-minute demo of the app in action.

[![Agentic AI with Google ADK](doc/youtube.jpg)](https://www.youtube.com/watch?v=Toh2HwAzqHc "Agentic AI with Google ADK")

## 50,000-Foot Architecture

```mermaid
graph TD;
    RA[Root Agent]-->SA["Solution Architecture Agent(s)"];
    RA[Root Agent]-->C4["C4 Agent(s)"];
    SA-->LT([Local Tools]);
    C4-->LT(Local Tools);
    C4-->MCPT(Mermaid MCP Tool);
```

## 10,000-Foot Architecture

These agents work together to propose the best solution architecture for a given problem statement and
generates C4 system context and container diagrams.

![diagram.svg](doc/diagram.svg)

## Getting Started

### STEP 1: INSTALL PYTHON DEPENDENCIES

```shell
cd python/
pip install -r requirements.txt
```

### STEP 2: SETUP MODEL

#### Using Gemini in Vertex AI

- Log in to Google Cloud:

```shell
gcloud auth login && gcloud auth application-default login
```

- Create an .env file.
```shell
cp adk/.env.gemini.sample adk/.env

# replace `[PROJECT_ID]` in .env with your GCP project ID.
```

#### Using Ollama-Hosted Local Model

- Install and restart Ollama service:

```shell
brew install ollama
brew services restart ollama
```

- Pull a local model:

```shell
ollama pull qwen3:8b
```

- Create an .env file.
```shell
cp adk/.env.ollama.sample adk/.env

# Update MODEL in .env accordingly
```

### STEP 3: RUN THE BAD BOY

```shell
cd python/adk/
adk web
```

- Navigate to http://127.0.0.1:8000 and run the agent.

### STEP 4: ????

- ...

### STEP 5: PROFIT!

![panda-destruction.gif](doc/panda-destruction.gif)
