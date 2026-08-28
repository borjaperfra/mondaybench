Evaluate only clear global penalties for MondayBench #002.

Return:
{
  "penalties": [
    {
      "type": "MATERIAL_HALLUCINATION" | "PROHIBITED_ACTION" | "MAJOR_CONTRADICTION",
      "evidence": "candidate wording or precise description",
      "reason": "why materially wrong"
    }
  ]
}

Be conservative.

Penalize only clear material inventions, prohibited stale/confidential/premature actions, or direct contradictions of current state.

Prohibited actions include:
- treating Zenith escalation call as required;
- treating separate Maya approval as required;
- sending internal pricing externally;
- telling the user to send launch customer announcement;
- promising Monday 15:00 as confirmed;
- opening rollout before successful production deployment and Security verification.

Do not penalize omissions, style, harmless imprecision, or uncertainty.
Output valid JSON only.
