---
status: accepted
---

# Streamlit for the dashboard + chatbot, behind a clean backend boundary

Considered a separate React/Next.js frontend talking to a REST API versus a
Python-native UI in the same process as the agent/extraction logic. We're
using Streamlit: it gives a dataframe-based comparison dashboard and a chat
UI (`st.chat_message`) without building or maintaining a separate API
contract for a JS frontend, and one Python process is a simpler on-prem
story than a frontend+backend split — both matter given the competition's
tight timeline. The known tradeoff: Streamlit doesn't scale to many
concurrent users and is hard to make look custom, which matters if this
becomes the startup later. We're accepting that tradeoff for the
competition deliverable specifically, on the condition that the
agent/extraction/storage logic stays behind a clean internal API boundary
(called as functions now) so Streamlit can be swapped for a real frontend
later without touching the intelligence layers. Visual quality is handled
separately — the user has design skills installed (e.g. `impeccable`,
`high-end-visual-design`) to theme it away from default Streamlit styling.
