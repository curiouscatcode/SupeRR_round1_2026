"""
src/dashboard/data_loader.py
Streamlit cached data loading and caching utility for SupeRR Selector 2.0 dashboard.
"""

import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@st.cache_data
def load_official_top10(discipline: str) -> pd.DataFrame:
    """Load frozen Step 7.4 official Top 10 rankings."""
    if discipline.lower() == 'batting':
        path = os.path.join(BASE_DIR, 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_batting_rankings.csv')
    else:
        path = os.path.join(BASE_DIR, 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_bowling_rankings.csv')
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_full_metrics(discipline: str) -> pd.DataFrame:
    """Load full cohort precomputed dashboard metrics (297 batters or 292 bowlers)."""
    if discipline.lower() == 'batting':
        path = os.path.join(BASE_DIR, 'outputs', 'step_10_methodology_report', 'dashboard_batting_metrics.csv')
    else:
        path = os.path.join(BASE_DIR, 'outputs', 'step_10_methodology_report', 'dashboard_bowling_metrics.csv')
    df = pd.read_csv(path)
    return df

@st.cache_data
def get_eda_figures_catalog():
    """Catalog of all 14 publication figures from Step 8 EDA."""
    fig_dir = os.path.join(BASE_DIR, 'outputs', 'step_8_eda', 'figures')
    return [
        {
            'id': 'fig01',
            'title': 'Figure 1: Batting Top 20 Pressure Performance Rankings',
            'category': 'Rankings & Cutoffs',
            'file': os.path.join(fig_dir, 'fig01_batting_top20_rankings.png'),
            'desc': 'PWSVA shrunk scores with Kish ESS opportunity sizes, bootstrap 95% CIs, and the official Top 10 cutoff boundary highlighting Hendricks vs. Patidar.'
        },
        {
            'id': 'fig02',
            'title': 'Figure 2: Bowling Top 20 Pressure Performance Rankings',
            'category': 'Rankings & Cutoffs',
            'file': os.path.join(fig_dir, 'fig02_bowling_top20_rankings.png'),
            'desc': 'SBVA shrunk scores with Kish ESS, bootstrap 95% CIs, and the official Top 10 cutoff boundary highlighting Mujeeb vs. Mosaddek.'
        },
        {
            'id': 'fig03',
            'title': 'Figure 3: Batting Empirical Bayes Shrinkage vs. Sample Size',
            'category': 'Empirical Bayes & Shrinkage',
            'file': os.path.join(fig_dir, 'fig03_batting_score_vs_sample_size.png'),
            'desc': 'Raw score vs. Kish ESS showing hyperbolic shrinkage trajectory towards the cohort grand mean (mu = 0.0387).'
        },
        {
            'id': 'fig04',
            'title': 'Figure 4: Bowling Empirical Bayes Shrinkage vs. Sample Size',
            'category': 'Empirical Bayes & Shrinkage',
            'file': os.path.join(fig_dir, 'fig04_bowling_score_vs_sample_size.png'),
            'desc': 'Raw score vs. Kish ESS showing hyperbolic shrinkage trajectory towards the cohort grand mean (mu = 0.0402).'
        },
        {
            'id': 'fig05',
            'title': 'Figure 5: Batting Top 10 Bootstrap Uncertainty (95% CIs)',
            'category': 'Uncertainty & Robustness',
            'file': os.path.join(fig_dir, 'fig05_batting_uncertainty_top10.png'),
            'desc': 'Bca 95% bootstrap confidence intervals for the Top 10 batters across 2,000 resamples.'
        },
        {
            'id': 'fig06',
            'title': 'Figure 6: Bowling Top 10 Bootstrap Uncertainty (95% CIs)',
            'category': 'Uncertainty & Robustness',
            'file': os.path.join(fig_dir, 'fig06_bowling_uncertainty_top10.png'),
            'desc': 'Bca 95% bootstrap confidence intervals for the Top 10 bowlers across 2,000 resamples.'
        },
        {
            'id': 'fig07',
            'title': 'Figure 7: Alpha Parameter Sensitivity Bump Chart (1.00 vs 1.25)',
            'category': 'Uncertainty & Robustness',
            'file': os.path.join(fig_dir, 'fig07_alpha_sensitivity_slope.png'),
            'desc': 'Rank invariance across alpha = 1.00 and alpha = 1.25 demonstrating top-tier robustness.'
        },
        {
            'id': 'fig08',
            'title': 'Figure 8: Empirical Pressure Distribution across 186k Deliveries',
            'category': 'Pressure Distribution & Exposure',
            'file': os.path.join(fig_dir, 'fig08_pressure_distribution_deliveries.png'),
            'desc': 'Distribution of Pressure P across Innings 1 and Innings 2, showing right-skewed tail.'
        },
        {
            'id': 'fig09',
            'title': 'Figure 9: Top Players Pressure Exposure Profile',
            'category': 'Pressure Distribution & Exposure',
            'file': os.path.join(fig_dir, 'fig09_top_players_pressure_exposure.png'),
            'desc': 'Proportion of opportunities faced across pressure bands (Low, Moderate, High, Climax).'
        },
        {
            'id': 'fig10',
            'title': 'Figure 10: Batting Phase Performance Heatmap (PP, Mid, Death)',
            'category': 'Tactical Phase & Format',
            'file': os.path.join(fig_dir, 'fig10_batting_phase_heatmap.png'),
            'desc': 'Mean SVA performance partitioned across Powerplay, Middle, and Death overs.'
        },
        {
            'id': 'fig11',
            'title': 'Figure 11: Bowling Phase Performance Heatmap (PP, Mid, Death)',
            'category': 'Tactical Phase & Format',
            'file': os.path.join(fig_dir, 'fig11_bowling_phase_heatmap.png'),
            'desc': 'Mean SVA performance partitioned across Powerplay, Middle, and Death overs.'
        },
        {
            'id': 'fig12',
            'title': 'Figure 12: Format Consistency (IPL vs. T20I)',
            'category': 'Tactical Phase & Format',
            'file': os.path.join(fig_dir, 'fig12_format_comparison_dual_players.png'),
            'desc': 'Cross-format consistency showing performance stability across franchise and international arenas.'
        },
        {
            'id': 'fig13',
            'title': 'Figure 13: Population-Wide Score Distributions',
            'category': 'Population & Correlation',
            'file': os.path.join(fig_dir, 'fig13_population_score_distributions.png'),
            'desc': 'Histogram and kernel density of shrunk scores across all 297 batters and 292 bowlers.'
        },
        {
            'id': 'fig14',
            'title': 'Figure 14: Multidimensional Feature Correlations',
            'category': 'Population & Correlation',
            'file': os.path.join(fig_dir, 'fig14_multidimensional_correlations.png'),
            'desc': 'Correlation matrix between pressure metrics, sample size, and performance indices.'
        }
    ]
