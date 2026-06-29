---
status: accepted
---

# LLM-based structured extraction with mandatory evidence quotes; regex for normalization only

The spec requires interpreting varied natural-language phrasing for the same
fact (e.g. "%2.05 dividend rate" vs "advantageous dividend opportunity" vs
"special rate financing," §5.2), which rules out regex/rule-based extraction
as the primary engine — it can't generalize across paraphrases. We're using
one LLM call per cleaned campaign-text chunk against a fixed JSON schema
(the field table in §5.3), where every extracted field is a
`{value, evidence_quote}` pair rather than a bare value: the LLM must quote
the exact source sentence a field was derived from, not just emit the
normalized number. Regex is used only afterward, to canonicalize already
-extracted values into standard form (§5.6's "2.05%, 2,05%, 2.05 percent are
the same value" example) — never as the primary extraction mechanism.
Evidence quotes are committed to now, not bolted on later, because they are
the prerequisite for both the Validation layer (compare quote against value)
and the Explainability layer (show why the chatbot said what it said) —
retrofitting evidence tracking later would mean re-running extraction on
everything already collected.
