You are classifying whether a quoted passage actually belongs in the cited legal provision. You will receive a citation and a quoted passage.

Return a JSON object with two fields:
- "reasoning": 2-4 sentences of step-by-step analysis
- "predicted_status": exactly one of VERIFIED, NOT_FOUND, MISATTRIBUTED, CITATION_UNRESOLVED

Decision procedure:

Step 1 - Is the citation itself real?
If the citation looks malformed, points to a nonexistent section, rule, or title, has an impossible subsection depth, or uses a section number far outside the normal range for that act or title, choose CITATION_UNRESOLVED.
Do not choose this just because you are unfamiliar with the provision. Choose it only when the citation structure itself is broken or the provision demonstrably cannot exist.

Step 2 - Does the quoted text belong in that exact provision?
If the quoted text reads like actual statutory or rule language that could sit verbatim inside the cited provision, choose VERIFIED.
Fragments, mid-sentence clips, enumerated items like (a) or (1), and text with structural markers are all normal quoting patterns. Fragmentary formatting alone is never evidence against VERIFIED.

Step 3 - Is the quote real provision text from somewhere else?
If the quote reads like genuine enacted language but from a different section, subsection, rule, or title than the one cited, choose MISATTRIBUTED.
The strongest signal is operative legal language such as "shall", "may", "must", or "is entitled to" in a way that sounds enacted, but the specific rule described does not match what the cited provision covers.

Step 4 - Default to NOT_FOUND.
If the citation looks real but the quote seems fabricated, paraphrased, subtly altered, or not traceable to any real provision, choose NOT_FOUND.

Key calibration rules:
- Similar topic or same act family is not enough for VERIFIED. The quote must be plausible as verbatim text from that exact provision.
- A single changed operative word can make the row NOT_FOUND.
- Use MISATTRIBUTED only when the quote clearly reads like genuine enacted text that belongs to a different provision.
- Use CITATION_UNRESOLVED only when the citation is structurally broken or points to a demonstrably nonexistent provision.
- Illinois administrative code citations like "XX Ill. Adm. Code NNNN.NN" are not malformed just because they are less familiar than ILCS or federal-rule citations.
