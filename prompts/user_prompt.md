Classify this citation-and-quote pair. Return JSON with "reasoning" and "predicted_status" fields.

Examples:

Example 1 - VERIFIED:
Citation: 20 ILCS 220/4
Quote: The United States and the Secretary of Agriculture thereof shall be free from liability by virtue of any transfer of the assets of the Illinois Rural Rehabilitation Corporation pursuant to this Act.
Answer: {{"reasoning": "This is a real citation, and the quoted sentence matches the cited provision as written.", "predicted_status": "VERIFIED"}}

Example 2 - NOT_FOUND:
Citation: 20 ILCS 220/4
Quote: The United States or the Secretary of Agriculture thereof shall be free from liability by virtue of any transfer of the assets of the Illinois Rural Rehabilitation Corporation pursuant to this Act.
Answer: {{"reasoning": "This is a real citation, but the quote is altered and does not match the cited provision's actual text.", "predicted_status": "NOT_FOUND"}}

Example 3 - VERIFIED:
Citation: 42 U.S.C. § 6634
Quote: (b) If the President determines that it is advantageous for the Committee to continue in being, (1) the Committee shall exercise such functions as are prescribed by the President; and (2) the members of the Committee shall serve at the pleasure of the President.
Answer: {{"reasoning": "This is a real citation, and the quoted statutory language is supported by the cited provision.", "predicted_status": "VERIFIED"}}

Example 4 - MISATTRIBUTED:
Citation: 810 ILCS 5/2A-532
Quote: (2) Acceptance of a part of any commercial unit is acceptance of that entire unit.
Answer: {{"reasoning": "This quote is real legal text, but it belongs to a different nearby provision rather than the citation shown here.", "predicted_status": "MISATTRIBUTED"}}

Example 5 - CITATION_UNRESOLVED:
Citation: Fed. R. Evid. 1502
Quote: Need for Personal Knowledge A witness may testify to a matter only if evidence is introduced sufficient to support a finding that the witness has personal knowledge of the matter.
Answer: {{"reasoning": "This quote is real, but the rule citation is impossible as written and does not resolve to a real provision.", "predicted_status": "CITATION_UNRESOLVED"}}

Example 6 - VERIFIED:
Citation: 810 ILCS 5/2-606
Quote: (2) Acceptance of a part of any commercial unit is acceptance of that entire unit.
Answer: {{"reasoning": "This is a real citation, and the quoted enumerated sentence is actually found in the cited provision.", "predicted_status": "VERIFIED"}}

Example 7 - NOT_FOUND:
Citation: 810 ILCS 5/2A-522
Quote: (2) A lessee acquires the right to recover goods identified to a lease contract only unless they conform to the lease contract.
Answer: {{"reasoning": "This is a real citation, but the quote changes the operative text of the provision and is not actually found there.", "predicted_status": "NOT_FOUND"}}

---

Now classify this row:

Citation: {citation}
Quoted passage: {quote}
