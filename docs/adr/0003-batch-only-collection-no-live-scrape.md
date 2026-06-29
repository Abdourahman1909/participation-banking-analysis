---
status: accepted
---

# Collection is scheduled-batch only; the agent never live-scrapes

Considered a hybrid where the chatbot/agent could fall back to scraping a
page live mid-conversation (the common "query_vector_db / query_sql_db /
live_scrape" agent-tool pattern). Rejected for this project: campaign terms
don't change minute-to-minute, so a few hours of staleness costs nothing,
while live scraping inside a chat turn adds multi-second latency and a new
live failure mode (site down, layout changed) at the exact moment a judge is
watching the demo. It also weakens the on-prem story — "the agent reaches
out to live bank websites per question" is a worse security posture than "a
scheduled job runs inside the network on a timer." Collection only happens
via a scheduled run (cron) or a manual developer-triggered refresh; the
agent's tools never include a scrape action.
