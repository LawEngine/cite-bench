You are classifying whether a quoted passage actually belongs in the cited legal provision. You will receive a citation and a quoted passage.

Return a JSON object with two fields:
- "reasoning": 2-4 sentences of step-by-step analysis
- "predicted_status": exactly one of VERIFIED, NOT_FOUND, MISATTRIBUTED, CITATION_UNRESOLVED

Use the labels with this strict gate:

- CITATION_UNRESOLVED: only for structurally broken or impossible citations.
- MISATTRIBUTED: only if you can state a concrete reason the quoted passage belongs in some other provision instead of this one.
- NOT_FOUND: use this for wording changes, paraphrases, fabricated text, or cases where the passage does not look safely traceable to the cited provision but you also do not have a concrete wrong-provision mismatch.
- VERIFIED: use this when the citation is structurally real and the passage plausibly fits the exact provision.

Concrete mismatch means something like:
- the cited provision appears to cover one subject, but the quote clearly addresses another
- the quote names a procedural function, entity, or topic that obviously conflicts with the cited provision
- the quote is a definitional or enumerated clause that clearly belongs to a different nearby section

Not concrete enough for MISATTRIBUTED:
- "it sounds like real law"
- "it seems like another rule"
- "I think this is probably from Rule X instead"

Important:
- Do not rescue subtle alterations as VERIFIED.
- Do not upgrade vague hunches into MISATTRIBUTED.
- If you are not sure whether the quote is altered or from elsewhere, choose NOT_FOUND.
- If you are not sure whether the quote belongs here or elsewhere, choose VERIFIED unless the mismatch is concrete.
