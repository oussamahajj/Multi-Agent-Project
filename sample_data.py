"""
Sample Data Generator for Multi-Agent Industrial Monitoring System
Generates realistic industrial machine data for testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional


def generate_sample_data(n_machines: int = 50, seed: int = 42) -> pd.DataFrame:
    """
    Generate sample industrial machine data for testing.
    
    Args:
        n_machines: Number of machines to generate
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with simulated machine data
    """
    np.random.seed(seed)
    
    # Machine types with their characteristics
    machine_types = {
        'CNC': {'temp_range': (35, 75), 'vib_range': (0.5, 4.0), 'power_range': (15, 80)},
        'Lathe': {'temp_range': (30, 65), 'vib_range': (0.3, 3.5), 'power_range': (10, 50)},
        'Press': {'temp_range': (25, 55), 'vib_range': (1.0, 6.0), 'power_range': (50, 200)},
        'Robot': {'temp_range': (28, 50), 'vib_range': (0.2, 2.0), 'power_range': (5, 30)},
        'Conveyor': {'temp_range': (20, 45), 'vib_range': (0.1, 1.5), 'power_range': (3, 15)},
        'Compressor': {'temp_range': (40, 90), 'vib_range': (0.8, 5.0), 'power_range': (20, 100)},
        'Pump': {'temp_range': (30, 70), 'vib_range': (0.4, 3.0), 'power_range': (8, 40)},
        'Mill': {'temp_range': (35, 80), 'vib_range': (0.6, 4.5), 'power_range': (25, 120)}
    }
    
    data = []
    
    for i in range(n_machines):
        machine_type = np.random.choice(list(machine_types.keys()))
        specs = machine_types[machine_type]
        
        # Determine machine health state (affects all metrics)
        health_state = np.random.choice(['excellent', 'good', 'fair', 'poor', 'critical'], 
                                        p=[0.15, 0.35, 0.30, 0.15, 0.05])
        
        # Health multipliers
        health_multipliers = {
            'excellent': {'temp': 0.7, 'vib': 0.5, 'error': 0.1},
            'good': {'temp': 0.85, 'vib': 0.7, 'error': 0.3},
            'fair': {'temp': 1.0, 'vib': 1.0, 'error': 0.5},
            'poor': {'temp': 1.2, 'vib': 1.5, 'error': 0.8},
            'critical': {'temp': 1.4, 'vib': 2.0, 'error': 1.0}
        }
        mult = health_multipliers[health_state]
        
        # Installation year (older machines tend to have more issues)
        installation_year = np.random.randint(2010, 2024)
        age = 2024 - installation_year
        age_factor = 1 + (age * 0.02)  # 2% degradation per year
        
        # Operational hours
        max_hours = age * 365 * 24 * 0.7  # 70% max utilization over years
        operational_hours = np.random.uniform(1000, max(1000, max_hours))
        
        # Temperature with health and age factors
        temp_base = np.random.uniform(*specs['temp_range'])
        temperature = temp_base * mult['temp'] * age_factor
        
        # Vibration with health and age factors
        vib_base = np.random.uniform(*specs['vib_range'])
        vibration = vib_base * mult['vib'] * age_factor
        
        # Sound level (correlated with vibration)
        sound = 60 + vibration * 10 + np.random.normal(0, 5)
        
        # Oil and coolant levels
        oil_level = np.random.uniform(60, 100) / age_factor
        coolant_level = np.random.uniform(50, 100) / age_factor
        
        # Power consumption
        power_base = np.random.uniform(*specs['power_range'])
        power_consumption = power_base * (1 + mult['vib'] * 0.1)  # Damaged machines use more power
        
        # Maintenance data
        last_maintenance_days = np.random.exponential(60) * age_factor
        maintenance_count = int(age * np.random.uniform(2, 6))
        failure_count = int(mult['error'] * age * np.random.uniform(0.5, 2))
        
        # AI supervision
        ai_supervision = np.random.choice([0, 1], p=[0.3, 0.7])
        
        # Error codes
        error_codes = int(np.random.exponential(2) * mult['error'])
        
        # Remaining useful life (inversely related to health)
        rul_base = {'excellent': 365, 'good': 180, 'fair': 90, 'poor': 30, 'critical': 7}
        remaining_life = rul_base[health_state] * np.random.uniform(0.8, 1.2)
        
        # Failure prediction
        failure_prob = {'excellent': 0.01, 'good': 0.05, 'fair': 0.15, 'poor': 0.40, 'critical': 0.70}
        failure_within_7_days = int(np.random.random() < failure_prob[health_state])
        
        # Machine type specific columns
        type_specific = {}
        if machine_type == 'CNC':
            type_specific['Spindle_Speed_RPM'] = np.random.uniform(1000, 12000) / mult['vib']
            type_specific['Tool_Wear_pct'] = np.random.uniform(10, 90) * mult['error']
        elif machine_type == 'Robot':
            type_specific['Joint_Accuracy_mm'] = np.random.uniform(0.01, 0.5) * mult['vib']
            type_specific['Cycle_Time_sec'] = np.random.uniform(5, 60) * mult['temp']
        elif machine_type == 'Compressor':
            type_specific['Pressure_Bar'] = np.random.uniform(6, 12) / mult['vib']
            type_specific['Air_Flow_m3h'] = np.random.uniform(100, 500) / mult['temp']
        
        machine_data = {
            'Machine_ID': f'M{str(i+1).zfill(4)}',
            'Machine_Type': machine_type,
            'Installation_Year': installation_year,
            'Operational_Hours': round(operational_hours, 1),
            'Temperature_C': round(min(150, max(0, temperature)), 1),
            'Vibration_mms': round(min(50, max(0, vibration)), 2),
            'Sound_dB': round(min(120, max(30, sound)), 1),
            'Oil_Level_pct': round(min(100, max(0, oil_level)), 1),
            'Coolant_Level_pct': round(min(100, max(0, coolant_level)), 1),
            'Power_Consumption_kW': round(min(500, max(1, power_consumption)), 1),
            'Last_Maintenance_Days_Ago': int(min(365, last_maintenance_days)),
            'Maintenance_History_Count': maintenance_count,
            'Failure_History_Count': failure_count,
            'AI_Supervision': ai_supervision,
            'Error_Codes_Last_30_Days': error_codes,
            'Remaining_Useful_Life_days': int(max(1, remaining_life)),
            'Failure_Within_7_Days': failure_within_7_days,
            **type_specific
        }
        
        data.append(machine_data)
    
    df = pd.DataFrame(data)
    
    # Add some intentional anomalies for testing
    # Extremely high temperature
    if len(df) > 5:
        df.loc[np.random.randint(0, len(df)), 'Temperature_C'] = 120.5
        df.loc[np.random.randint(0, len(df)), 'Vibration_mms'] = 15.8
        df.loc[np.random.randint(0, len(df)), 'Power_Consumption_kW'] = 350.0
        df.loc[np.random.randint(0, len(df)), 'Error_Codes_Last_30_Days'] = 25
        df.loc[np.random.randint(0, len(df)), 'Last_Maintenance_Days_Ago'] = 300
    
    return df


def save_sample_data(filepath: str = "sample_data.csv", n_machines: int = 50):
    """Generate and save sample data to a CSV file."""
    df = generate_sample_data(n_machines)
    df.to_csv(filepath, index=False)
    print(f"✅ Sample data generated: {filepath}")
    print(f"   - {len(df)} machines")
    print(f"   - {len(df.columns)} columns")
    return df


if __name__ == "__main__":
    # Generate sample data when run directly
    df = save_sample_data("sample_industrial_data.csv", n_machines=75)
    print("\nData Preview:")
    print(df.head())
    print("\nColumn Types:")
    print(df.dtypes)
    print("\nStatistics:")
    print(df.describe())
