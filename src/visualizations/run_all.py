"""
Master Visualization Runner
===========================
Executes all visualization modules:
1. plot_pressure_analysis.py -> Charts 01-05
2. plot_batter_analysis.py   -> Charts 06-10
3. plot_bowler_analysis.py   -> Charts 11-15
4. plot_phase_specialists.py -> Chart 16

Saves all high-resolution figures (300 DPI) to outputs/visualizations/
"""

import sys
from pathlib import Path

# Add current directory to path
curr_dir = Path(__file__).resolve().parent
sys.path.append(str(curr_dir))

from plot_pressure_analysis import (
    plot_batting_pi_distribution, plot_bowling_pi_distribution,
    plot_pressure_by_phase, plot_pressure_by_innings, plot_match_timelines
)
from plot_batter_analysis import (
    plot_batter_strike_rate_comparison, plot_batter_survival_rate_comparison,
    plot_batter_boundary_dot_comparison, plot_top10_batters_brs, plot_top10_batter_components
)
from plot_bowler_analysis import (
    plot_bowler_economy_comparison, plot_bowler_wicket_rate_comparison,
    plot_bowler_dot_boundary_comparison, plot_top10_bowlers_bors, plot_top10_bowler_components
)
from plot_phase_specialists import plot_phase_specialists_grid


def run_all():
    print("=================================================================")
    print("RUNNING ALL CRICKET ANALYTICS VISUALIZATION SCRIPTS")
    print("=================================================================")
    
    print("\n--- Part A: Pressure Analysis ---")
    plot_batting_pi_distribution()
    plot_bowling_pi_distribution()
    plot_pressure_by_phase()
    plot_pressure_by_innings()
    plot_match_timelines()
    
    print("\n--- Part B: Batter Analysis ---")
    plot_batter_strike_rate_comparison()
    plot_batter_survival_rate_comparison()
    plot_batter_boundary_dot_comparison()
    plot_top10_batters_brs()
    plot_top10_batter_components()
    
    print("\n--- Part C: Bowler Analysis ---")
    plot_bowler_economy_comparison()
    plot_bowler_wicket_rate_comparison()
    plot_bowler_dot_boundary_comparison()
    plot_top10_bowlers_bors()
    plot_top10_bowler_components()
    
    print("\n--- Part D: Phase Specialist Analysis ---")
    plot_phase_specialists_grid()
    
    print("\n=================================================================")
    print("ALL 16 CHARTS SUCCESSFULLY GENERATED IN outputs/visualizations/")
    print("=================================================================")


if __name__ == '__main__':
    run_all()
