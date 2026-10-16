154 minutes was the median reported ED time across 4,052 U.S. hospitals in my latest healthcare analytics project.

But the number I found most important was 64.9%.

That was the share of facilities with a usable psychiatric-patient ED time measure in the July 2026 CMS Care Compare release.

I built a reproducible workflow using Python and DuckDB SQL to examine hospital-level ED throughput, volume, state patterns and reporting completeness.

Three findings stood out:

• Median ED time increased from 128 minutes in low-volume departments to 197 minutes in very-high-volume departments.
• Among states with at least 20 reporting hospitals, Maryland had the highest median at 249 minutes.
• Psychiatric-patient and transfer measures were available for only 64.9% and 50.8% of facilities, respectively.

I also kept two national-looking numbers separate on purpose.

The 154-minute value is an unweighted median of hospital medians. CMS publishes a national OP-18a score of 168 minutes. They answer different questions and should not be treated as interchangeable.

The repository includes source acquisition, SHA-256 manifests, DuckDB transformations, QA checks, bootstrap confidence intervals, a Kruskal–Wallis test, benchmark tables, automated tests and a dashboard.

This is descriptive benchmarking—not a hospital ranking or a causal analysis. Public data cannot explain acuity, staffing, boarding or local capacity.

What would you add before using public ED measures for an operational decision?

P.S. I’ll add the complete GitHub project in the first comment.

#HealthcareAnalytics #PublicHealth

