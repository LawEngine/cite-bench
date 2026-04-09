Classify this citation-and-quote pair. Return JSON with "reasoning" and "predicted_status" fields.

Examples:

Example 1 - VERIFIED:
Citation: 42 U.S.C. § 6634
Quoted passage: (b) If the President determines that it is advantageous for the Committee to continue in being, (1) the Committee shall exercise such functions as are prescribed by the President; and (2) the members of the Committee shall serve at the pleasure of the President.
Answer: {{"reasoning": "This is a real citation, and the quoted statutory language is supported by the cited provision.", "predicted_status": "VERIFIED"}}

Example 2 - NOT_FOUND:
Citation: 810 ILCS 5/2A-522
Quoted passage: (2) A lessee acquires the right to recover goods identified to a lease contract only unless they conform to the lease contract.
Answer: {{"reasoning": "This is a real citation, but the quote changes the operative text of the provision and is not actually found there.", "predicted_status": "NOT_FOUND"}}

Example 3 - MISATTRIBUTED:
Citation: 810 ILCS 5/2A-532
Quoted passage: (2) Acceptance of a part of any commercial unit is acceptance of that entire unit.
Answer: {{"reasoning": "This quote is real legal text, but it belongs to a different nearby provision rather than the citation shown here.", "predicted_status": "MISATTRIBUTED"}}

Example 4 - CITATION_UNRESOLVED:
Citation: Fed. R. Evid. 1502
Quoted passage: Need for Personal Knowledge A witness may testify to a matter only if evidence is introduced sufficient to support a finding that the witness has personal knowledge of the matter.
Answer: {{"reasoning": "This quote is real, but the rule citation is impossible as written and does not resolve to a real provision.", "predicted_status": "CITATION_UNRESOLVED"}}

When unsure:
- vague hunch that the quote belongs elsewhere -> do not use MISATTRIBUTED
- visible wording change or paraphrase -> use NOT_FOUND
- structurally real citation and plausible exact fit -> use VERIFIED

Citation: {citation}
Quoted passage: {quote}
