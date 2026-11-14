# Audit Investigation 5: Phase Exposure Confounding & Specialization Audit

## Executive Summary

Step 11 concluded that the official v2.0 rankings are confounded by match phase exposure, explaining that MS Dhoni's #1 overall ranking ($	ext{BRS} = 95.05$) is driven by a heavy death-overs concentration (78.4% of balls) where strike rates are naturally elevated, despite an abysmal middle-overs strike rate of 65.79 (#86 in middle overs).

### Independent Audit Conclusions:
1. **MS Dhoni's Phase Numbers are 100% Confirmed:**
   - High-Pressure Balls Faced: **194 balls**.
   - Death Overs: **152 balls (78.35%)** | Strike Rate = **197.37** (vs league mean 145.1).
   - Middle Overs: **38 balls (19.59%)** | Strike Rate = **65.79** (vs league mean 109.1).
   - Powerplay: **4 balls (2.06%)** | Strike Rate = **150.00**.
   - Overall High-Pressure Strike Rate: **170.62**.
2. **Phase Exposure Confounding is a Real Statistical Phenomenon:**
   - In T20 cricket, high-pressure strike rates differ systematically by phase: Middle Overs average is **109.1**, while Death Overs average is **145.1** (a $+36.0$ point spread).
   - Batters who face 70–80% of their high-pressure balls in the death overs naturally accumulate higher aggregate strike rates than anchors who face high pressure in the middle overs.
3. **Critical Cricketing Nuance: Overall Reliability vs Relative Specialization:**
   - **Should we standardize metrics by phase in the overall model?**
   - **No.** Standardizing by phase equates middle-overs accumulation with death-overs finishing. In T20 match chasing, finishing a match requires an absolute strike rate of 180–200+ under intense fielding restrictions and boundary demands. A team cannot substitute a middle-overs anchor for a death-overs finisher.
   - Dhoni's #1 ranking is **not a calculation error**; it accurately reflects his status as the premier death-overs match finisher in high-pressure situations.
   - The appropriate architectural solution is **not to distort the overall ranking with artificial phase z-scores**, but to maintain **dedicated phase specialist leaderboards** alongside the overall reliability leaderboard.

---
*(Report generated automatically by Step 11.2 Independent Audit - Investigation 5)*