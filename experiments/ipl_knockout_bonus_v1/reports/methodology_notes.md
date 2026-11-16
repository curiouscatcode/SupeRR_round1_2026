# Methodology Notes: IPL Knockout Multiplier Accounting

**Experiment:** IPL Knockout Bonus (v1)  
**Author:** Antigravity (Google DeepMind Agentic System)  
**Date:** November 15, 2026  
**Status:** Certified Methodological Specification  

---

## 1. Mathematical Architecture

The IPL Knockout Bonus experiment evaluates the effect of scaling delivery-level pressure weights for deliveries bowled or faced in official IPL playoff matches (Qualifier 1, Eliminator, Qualifier 2, and Final).

### 1.1 Multiplier Weight Adjustment
For any delivery $i$, let $P_i \in [0, 100]$ be the frozen pre-delivery match pressure index. The baseline delivery weight ($\alpha = 1.00$) is:
$$w_i^{\text{base}} = \frac{P_i}{50.0}$$

Under an experimental knockout multiplier $M \in \{1.10, 1.20, 1.25\}$:
$$w_i^{\text{adj}} = \begin{cases} w_i^{\text{base}} \times M & \text{if } \text{match\_id}_i \in \mathcal{K} \\ w_i^{\text{base}} \times 1.00 & \text{otherwise} \end{cases}$$
where $\mathcal{K}$ represents the set of 19 audited, pure 20-over IPL playoff matches.

---

## 2. Aggregation & Performance Accounting

### 2.1 Batting (PWSVA)
Batting is evaluated strictly per ball faced (`is_batter_ball_faced == True`):
- Delivery Value Added:
  $$v_{\text{bat}, i} = (\text{batter\_runs}_i - \mu_R(c_i)) - \lambda_{\text{eff}, i} \cdot (\text{is\_striker\_dismissed}_i - \mu_W(c_i))$$
- Player-level weighted sums:
  $$S_w = \sum_{i \in \text{faced}} w_i^{\text{adj}}, \quad S_{w2} = \sum_{i \in \text{faced}} (w_i^{\text{adj}})^2, \quad S_{wv} = \sum_{i \in \text{faced}} w_i^{\text{adj}} \cdot v_{\text{bat}, i}$$
- Raw PWSVA:
  $$\text{Raw Score} = \frac{S_{wv}}{S_w}$$
- Kish Effective Sample Size ($\text{ESS}$):
  $$\text{ESS}_{\text{adj}} = \frac{S_w^2}{S_{w2}}$$
- Empirical Bayes Shrinkage ($K_{\text{bat}} = 600$):
  $$\text{Shrunk Score} = \text{Raw Score} \times \frac{\text{ESS}_{\text{adj}}}{\text{ESS}_{\text{adj}} + 600.0}$$

### 2.2 Bowling (SBVA)
Bowling uses legal-ball quota accounting:
- Legal deliveries accumulate expected runs and wickets; non-legal deliveries (wides, no-balls) accumulate negative runs conceded and bonus wicket credits.
- Denominator and Kish ESS accumulate over legal balls only:
  $$S_{w, \text{leg}} = \sum_{i \in \text{legal}} w_i^{\text{adj}}, \quad S_{w2, \text{leg}} = \sum_{i \in \text{legal}} (w_i^{\text{adj}})^2, \quad S_{wv, \text{tot}} = \sum_{i \in \text{all}} w_i^{\text{adj}} \cdot v_{\text{bowl}, i}$$
- Raw SBVA:
  $$\text{Raw Score} = \frac{S_{wv, \text{tot}}}{S_{w, \text{leg}}}$$
- Kish Effective Sample Size ($\text{ESS}$):
  $$\text{ESS}_{\text{adj}} = \frac{S_{w, \text{leg}}^2}{S_{w2, \text{leg}}}$$
- Empirical Bayes Shrinkage ($K_{\text{bowl}} = 500$):
  $$\text{Shrunk Score} = \text{Raw Score} \times \frac{\text{ESS}_{\text{adj}}}{\text{ESS}_{\text{adj}} + 500.0}$$

---

## 3. Mathematical Proof of Zero-Knockout Invariance

For any player $p$ who faced or bowled 0 deliveries in $\mathcal{K}$:
$$\forall i \in \mathcal{D}_p, \quad \text{match\_id}_i \notin \mathcal{K} \implies w_i^{\text{adj}} = w_i^{\text{base}} \times 1.00 = w_i^{\text{base}}$$
Therefore:
$$S_w^{\text{adj}} \equiv S_w^{\text{base}}, \quad S_{w2}^{\text{adj}} \equiv S_{w2}^{\text{base}}, \quad S_{wv}^{\text{adj}} \equiv S_{wv}^{\text{base}}$$
It follows immediately that:
$$\text{Raw Score}^{\text{adj}} \equiv \text{Raw Score}^{\text{base}}, \quad \text{ESS}_{\text{adj}} \equiv \text{ESS}_{\text{base}}, \quad \text{Shrunk Score}^{\text{adj}} \equiv \text{Shrunk Score}^{\text{base}}$$
This analytical identity ensures that zero-knockout players experience zero score inflation or deflation, maintaining absolute fairness across tournament structures.
