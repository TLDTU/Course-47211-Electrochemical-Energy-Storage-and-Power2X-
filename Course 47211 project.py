import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.stats.power as smp

# We define data types for the relevant columns
dtype_spec = {
    'PriceArea': 'str', 
    'TotalLoad': 'str', 
    'Biomass': 'str', 
    'FossilGas': 'str', 
    'FossilHardCoal': 'str', 
    'FossilOil': 'str', 
    'HydroPower': 'str', 
    'OtherRenewable': 'str', 
    'SolarPower': 'str', 
    'Waste': 'str', 
    'OnshoreWindPower': 'str', 
    'OffshoreWindPower': 'str', 
    'ExchangeContinent': 'str', 
    'ExchangeGreatBelt': 'str', 
    'ExchangeNordicCountries': 'str', 
    'ExchangeGreatBritain': 'str'
}

# We load the data with specified data types and handle large files
df = pd.read_csv('ElectricityBalanceNonv.csv', sep=';', dtype=dtype_spec, low_memory=False)

# We convert 'HourUTC' and 'HourDK' to datetime
df['HourUTC'] = pd.to_datetime(df['HourUTC'], format='%Y-%m-%d %H:%M')
df['HourDK'] = pd.to_datetime(df['HourDK'], format='%Y-%m-%d %H:%M')
df_subset = df[(df['HourDK'] >= '2023-01-11') & (df['HourDK'] <= '2024-10-31')]

# We replace commas with dots in numeric columns
df.replace(',', '.', regex=True, inplace=True)

# We list of numeric columns
numeric_columns = ['TotalLoad', 'Biomass', 'FossilGas', 'FossilHardCoal', 'FossilOil', 
                   'HydroPower', 'OtherRenewable', 'SolarPower', 'Waste', 
                   'OnshoreWindPower', 'OffshoreWindPower', 'ExchangeContinent', 
                   'ExchangeGreatBelt', 'ExchangeNordicCountries', 'ExchangeGreatBritain']

# We convert numeric columns to float using pd.to_numeric and coerce errors
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# 1. Create 'totalwind' (OnshoreWindPower + OffshoreWindPower)
df['totalwind'] = df['OnshoreWindPower'] + df['OffshoreWindPower']

# 2. Create 'solarandwind' (totalwind + SolarPower) + Hydro (even though it is part of the reneawble)
df['solarandwind'] = (df['totalwind'] + df['SolarPower'])

# 3. Create 'energyconsumption' (TotalLoad - Biomass)
df['energyconsumption'] = df['TotalLoad'] - df['Biomass']

# 4. Create 'prosumption' (solarandwind - energyconsumption)
df['prosumption_before_scale'] = df['solarandwind'] - df['energyconsumption']

# Calculate the scaling factor (solarandwind*k=energyconsumtion)
scaling_factor = (df['energyconsumption'].sum()) / (df['solarandwind'].sum())

# Print the sums and scaling factor, converting to string where necessary
print("Sum of Energy Consumption: " + str(df['energyconsumption'].sum())+"MWh")
print("Sum of Solar and Wind: " + str(df['solarandwind'].sum())+ "MWh")  # Correcting to use total_wind_solar
print("The scaling factor: " + str(scaling_factor))

#5. Create 'scaled_solarwind' (solarwind*scaling_factor)
df['scaled_solarandwind'] = (df['solarandwind']*scaling_factor)

# Now we can plot or analyze these time series
print(df[['HourDK', 'totalwind', 'solarandwind', 'energyconsumption', 'prosumption_before_scale','scaled_solarandwind']].head())


# Plotting the 4 variables over time
plt.figure(figsize=(14, 8))
#plt.plot(df['HourDK'], df['totalwind'], label='Total Wind Power')
plt.plot(df['HourDK'], df['solarandwind'], label='Solar and Wind Power')
plt.plot(df['HourDK'], df['energyconsumption'], label='Energy Consumption')
plt.plot(df['HourDK'], df['scaled_solarandwind'], label='Scaled Solar and Wind Power')
#plt.plot(df['HourDK'], df['prosumption'], label='Prosumption')

# Formatting the plot
plt.title('Time Series of Wind, Solar, Energy Consumption, and Prosumption')
plt.xlabel('Time (HourDK)')
plt.ylabel('Power (MWh)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)

# Show plot
plt.tight_layout()
plt.show()