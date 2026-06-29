---
status: accepted
---

# campaign_type is a closed enum, not LLM-generated free text

The spec names 8 campaign types (§5.4) and scores both "Determining the
Campaign Type" and "Comparing similar products" (§7, Functionality 20%).
Open free text breaks comparison immediately — Bank A writing "Housing
Finance Campaign" and Bank B writing "Home Ownership Financing" for the same
concept can't be grouped without yet another normalization pass. We're
classifying every extraction into one of the spec's 8 named types plus an
`Other` catch-all, as a sub-task of the same extraction LLM call (give it
the fixed list, ask it to pick one) rather than a separate classifier model.
Descriptive fields that comparison doesn't depend on (campaign_advantage
text, target_audience notes) stay free text — only fields that grouping or
comparison relies on need to be closed.
