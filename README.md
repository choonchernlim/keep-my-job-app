# "Keep My Job" App


## Getting Started

- Log in to Google Cloud:

```shell
gcloud auth login && gcloud auth application-default login
```

- In `adk/`, rename `.env.sample` to `.env` and replace `[PROJECT_ID]` with your GCP project ID.

- Run the agents:

```shell
cd adk/
adk web --reload_agents
```

## Helpful Links

- [Developer’s guide to multi-agent patterns in ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/)