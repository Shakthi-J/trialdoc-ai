import numpy as np
from scipy import stats


def interpret_table(df):

    results = []

    for _, row in df.iterrows():
        results.append({
            "treatment": row["Treatment"],
            "sample_size": int(row["N"]),
            "mean": float(row["Mean_BP_Reduction"]),
            "std_dev": float(row["StdDev"])
        })

    placebo_mean = None
    placebo_std = None
    placebo_n = None
    best_mean = -999
    best_treatment = None

    for r in results:
        if r["treatment"].lower() == "placebo":
            placebo_mean = r["mean"]
            placebo_std = r["std_dev"]
            placebo_n = r["sample_size"]

        if r["mean"] > best_mean:
            best_mean = r["mean"]
            best_treatment = r["treatment"]

    # Conclusion
    if placebo_mean is not None and best_mean > placebo_mean:
        conclusion = "positive"
    else:
        conclusion = "negative"

    # Confidence score
    improvement = best_mean - placebo_mean if placebo_mean is not None else 0
    confidence_score = round(improvement / best_mean, 2) if best_mean != 0 else 0

    # Warning
    if improvement < 1:
        warning = "Low clinical significance"
    elif improvement < 3:
        warning = "Moderate effect"
    else:
        warning = "Strong clinical effect"

    # ⭐ T-test and p-value for each treatment vs placebo
    pairwise_stats = []

    if placebo_mean is not None:
        for r in results:
            if r["treatment"].lower() == "placebo":
                continue

            # Two-sample t-test using summary statistics (Welch's t-test)
            t_stat, p_value = stats.ttest_ind_from_stats(
                mean1=r["mean"],
                std1=r["std_dev"],
                nobs1=r["sample_size"],
                mean2=placebo_mean,
                std2=placebo_std,
                nobs2=placebo_n,
                equal_var=False  # Welch's t-test — does not assume equal variance
            )

            # Cohen's d effect size
            pooled_std = np.sqrt(
                ((r["sample_size"] - 1) * r["std_dev"] ** 2 +
                 (placebo_n - 1) * placebo_std ** 2) /
                (r["sample_size"] + placebo_n - 2)
            )
            cohens_d = round((r["mean"] - placebo_mean) / pooled_std, 3)

            # Significance label
            if p_value < 0.001:
                significance = "p < 0.001 (highly significant)"
            elif p_value < 0.01:
                significance = f"p = {round(p_value, 4)} (significant)"
            elif p_value < 0.05:
                significance = f"p = {round(p_value, 4)} (significant)"
            else:
                significance = f"p = {round(p_value, 4)} (not significant)"

            pairwise_stats.append({
                "treatment": r["treatment"],
                "vs": "Placebo",
                "t_statistic": round(t_stat, 4),
                "p_value": round(p_value, 6),
                "significance": significance,
                "cohens_d": cohens_d,
                "effect_size_label": (
                    "Large" if abs(cohens_d) >= 0.8 else
                    "Medium" if abs(cohens_d) >= 0.5 else
                    "Small"
                )
            })

    return {
        "endpoint": "Blood Pressure Reduction",
        "results": results,
        "best_treatment": best_treatment,
        "conclusion": conclusion,
        "confidence_score": confidence_score,
        "warning": warning,
        "pairwise_stats": pairwise_stats  # ⭐ new
    }