# "Keep My Job" App

Are you struggling to keep your job? Want to impress your boss and appear marginally more competent?
You are in the right place!

"Keep My Job" is an app that uses AI multi-agent systems to help you work faster and get more done.

## Solution Design Agents

These agents work together to propose the best solution architecture for a given problem statement.

![diagram.svg](doc/diagram.svg)


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