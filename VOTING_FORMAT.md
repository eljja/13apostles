# Voting and Decision Format

This document outlines the strict rules and formulas used by the 13 Apostles when voting on proposed candidates, as well as how the final selection is calculated.

## 1. Voting Rules for Each Apostle

Each of the 13 Apostles evaluates the candidates across **5 Categories**.
For each category, an Apostle is given **10 points** to distribute among the candidates, meaning each Apostle casts a total of **50 points**.

### Point Distribution Constraints:
1. **Total Points per Category:** Exactly 10 points must be distributed across candidates for each of the 5 categories.
2. **Maximum Points:** A maximum of **5 points** can be allocated to any single candidate in a given category.
3. **Distribution:** Points can (and should) be divided among multiple candidates based on their relative merits.
4. **Mandatory Reasoning:** Every point allocation MUST be accompanied by a clear, logical reason explaining *why* the candidate received those points in that category.

### The 5 Evaluation Categories:
1. **Expected Impact (기대효과 점수):** How much this candidate improves the system's utility.
2. **Feasibility (구현가능성 점수):** How realistic and practical the candidate is to implement.
3. **Goal Alignment (목표정렬 점수):** How well the candidate aligns with the *Cost-bounded Useful Adaptation* objective.
4. **Safety Multiplier (안전성 계수):** Evaluation of security, stability, and lack of harmful side effects.
5. **Cost Multiplier (비용 계수):** Evaluation of computational, developmental, and maintenance overhead.

---

## 2. Final Score Calculation

Once all 13 Apostles have cast their votes, the points for each candidate are aggregated per category. The final selection is determined by calculating the **Final Score** for each candidate using the following formula:

```text
Final Score = 
  ( Total Expected Impact Score )
  × ( Total Feasibility Score )
  × ( Total Goal Alignment Score )
  × ( Total Safety Multiplier )
  ÷ ( Total Cost Multiplier )
```

### Veto and Disqualification
* **Safety & Risk Veto:** If a candidate poses an extreme, irreversible threat, the Risk or Safety Apostle can invoke a **VETO**. A vetoed candidate is immediately disqualified, regardless of its Final Score.
* **Cost Division by Zero Prevention:** The system ensures the Total Cost Multiplier is never zero (minimum value of 1) to prevent mathematical errors.

### The Winner
The candidate with the highest **Final Score** (that has not been vetoed) is selected as the evolutionary path for the current generation.
