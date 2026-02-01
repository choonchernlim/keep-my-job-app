# "Keep My Job" App


## Getting Started

- Log in to Google Cloud:

```shell
gcloud auth login && gcloud auth application-default login
```

- Rename [.env.sample](python/adk/.env.sample) to [.env](python/adk/.env) and replace `[PROJECT_ID]` with your Google
  Cloud project ID.

- Run the agents:

```shell
cd python/adk
adk web --reload_agents
```