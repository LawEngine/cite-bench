Classify this citation-and-quote pair. Return JSON with "reasoning" and "predicted_status" fields.

Examples:

Example 1 - VERIFIED:
Citation: 735 ILCS 5/2-619(a)(9)
Quote: The court shall hear and determine the motion without a jury.
Answer: {{"reasoning": "Real ILCS citation for Section 2-619. The quoted text reads like verbatim statutory language about motion practice from that section.", "predicted_status": "VERIFIED"}}

Example 2 - NOT_FOUND (subtle word change):
Citation: 735 ILCS 5/2-619(a)(9)
Quote: The court may hear and determine the motion without a jury.
Answer: {{"reasoning": "Real citation, but 'may' instead of 'shall' is an operative word change. The actual provision uses 'shall'. This is fabricated text.", "predicted_status": "NOT_FOUND"}}

Example 3 - VERIFIED (fragment):
Citation: Fed. R. Civ. P. 56(a)
Quote: identifying each claim or defense - or the part of each claim or defense - on which summary judgment is sought
Answer: {{"reasoning": "Real FRCP citation. The quote is a mid-sentence fragment from Rule 56(a), which is a normal quoting pattern. Fragmentary formatting does not count against verification.", "predicted_status": "VERIFIED"}}

Example 4 - MISATTRIBUTED:
Citation: 735 ILCS 5/2-615
Quote: The court may dismiss the action or any claim against any defendant if the plaintiff fails to prosecute.
Answer: {{"reasoning": "Real citation for 2-615, which covers dismissal for insufficient pleading. But this quote describes involuntary dismissal for failure to prosecute, which belongs elsewhere, not in 2-615.", "predicted_status": "MISATTRIBUTED"}}

Example 5 - CITATION_UNRESOLVED:
Citation: 735 ILCS 5/2-619(a)(9)(z)(99)
Quote: The court shall hear and determine the motion without a jury.
Answer: {{"reasoning": "The base citation is real, but the extra subsection tail (z)(99) does not exist. This is a phantom citation.", "predicted_status": "CITATION_UNRESOLVED"}}

Example 6 - VERIFIED (enumerated item):
Citation: 750 ILCS 5/503(d)
Quote: (1) the duration of the marriage;
Answer: {{"reasoning": "Real citation for the marital property division statute. The quote is a single enumerated item from the list of factors in subsection (d). Single enumerated items are normal quote fragments.", "predicted_status": "VERIFIED"}}

Example 7 - NOT_FOUND (number change):
Citation: Fed. R. Civ. P. 12(a)(1)(A)
Quote: A defendant must serve an answer within 30 days after being served with the summons and complaint.
Answer: {{"reasoning": "Real citation, but the actual timeframe in FRCP 12(a)(1)(A) is 21 days, not 30 days. This is a fabricated alteration.", "predicted_status": "NOT_FOUND"}}

---

Now classify this row:

Citation: {citation}
Quoted passage: {quote}
