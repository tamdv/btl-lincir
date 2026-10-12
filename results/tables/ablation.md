# Ablation (trung bình qua seed; ngoặc: Δ so với baseline)

| Biến thể | InfoNCE (A) | Nhiễu có hướng (B) | FIQ TB R@10 | FIQ TB R@50 | CIRCO mAP@5 |
|---|---|---|---|---|---|
| Baseline (LinCIR) |  |  | 25.90 | 45.53 | 10.47 |
| A: + InfoNCE | ✓ |  | 25.54 (-0.36) | 45.16 (-0.37) | 8.02 (-2.45) |
| B: + nhiễu có hướng |  | ✓ | 26.50 (+0.60) | 46.79 (+1.26) | 10.94 (+0.47) |
| A+B | ✓ | ✓ | 25.44 (-0.46) | 45.36 (-0.17) | 7.81 (-2.66) |
