import netCDF4 as nc
import numpy as np
from datetime import datetime, timedelta
import math

import math
from datetime import datetime, time, timedelta

def calculate_solar_noon_utc(year, month, day, longitude, latitude):
  """
  Calculates the time of solar noon in Coordinated Universal Time (UTC).

  Solar noon is the time when the sun is at its highest point in the sky
  (transiting the local celestial meridian).

  This calculation depends on the date (for Equation of Time) and longitude.
  Latitude is not required for the *time* of solar noon, but is included
  in this function's parameters as requested.

  Args:
    year (int): The year (e.g., 2024).
    month (int): The month (1-12).
    day (int): The day (1-31).
    longitude (float): The observer's longitude in degrees.
                       (Positive for East, Negative for West).
    latitude (float): The observer's latitude in degrees (not used in this calc).

  Returns:
    float: The time of solar noon in UTC hours (e.g., 12.5 = 12:30 PM UTC).
  """
  
  # 1. Calculate the Day of the Year (DOY)
  d = datetime(year, month, day)
  doy = d.timetuple().tm_yday

  # 2. Calculate the Equation of Time (EoT) in minutes
  # This is a common approximation
  # B is in degrees
  B_deg = (360 / 365.24) * (doy - 81)
  # B is in radians
  B_rad = math.radians(B_deg)
  
  eot = 9.87 * math.sin(2 * B_rad) - 7.53 * math.cos(B_rad) - 1.5 * math.sin(B_rad)
  
  # 3. Calculate Solar Noon in minutes from UTC midnight
  # 720 = 12:00 (noon) in minutes (12 * 60)
  # 4 * longitude = longitude correction in minutes (Earth rotates 1 degree in 4 mins)
  # We subtract eot from the mean solar noon
  
  solar_noon_minutes_from_utc_midnight = 720 - (4 * longitude) - eot
  
  # 4. Convert the minutes into hours
  solar_noon_utc_hours = solar_noon_minutes_from_utc_midnight / 60
  
  return solar_noon_utc_hours



def calculate_vapor_pressure(dewpoint_k):
    """
    Convert Dewpoint Temperature (Kelvin) to Vapor Pressure (kPa)
    using the August-Roche-Magnus approximation.
    """
    # Convert Kelvin to Celsius
    dewpoint_c = dewpoint_k - 273.15
    
    # Constants for the formula
    a = 6.112  # hPa
    b = 17.67
    c = 243.5
    
    # Calculate saturation vapor pressure at dewpoint (which is actual vapor pressure)
    # Result in hPa
    es_hpa = a * np.exp((b * dewpoint_c) / (dewpoint_c + c))
    
    # Convert hPa to kPa (1 hPa = 0.1 kPa)
    return es_hpa * 0.1

def create_clm_file(input_filename, lon, lat,output_filename):
    """
    convert era5 climate forcing stored in file input_filename for 
    location specified by lon, lat to ecosim climate forcing
    specified by output_filename
    Args:
        input_filename(str): name of input file
        lon(float): longitude of the selected location
        lat(float): latitude of the selected location
        output_filename(str): name of the output file to be used by ecosim
    """
    print(f"Opening source file: {input_filename}")
    try:
        src = nc.Dataset(input_filename, 'r')
    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
        return

    # --- Read Source Variables ---
    print("Reading source data...")
    # Times are seconds since 1970-01-01
    valid_times = src.variables['valid_time'][:]
    
    # Meteorology variables
    t2m = src.variables['t2m'][:]  # Kelvin
    u10 = src.variables['u10'][:]  # m/s
    v10 = src.variables['v10'][:]  # m/s
    tp = src.variables['tp'][:]    # meters
    d2m = src.variables['d2m'][:]  # Kelvin
    ssrd = src.variables['ssrd'][:] # J/m^2 (Accumulated)
    sp = src.variables['sp'][:]    # Pa (Surface Pressure)

    src.close()

    # --- Process Time Dimensions ---
    print("Processing time dimensions...")
    # Convert valid_times to datetime objects
    base_date = datetime(1970, 1, 1)
    dates = [base_date + timedelta(seconds=int(t)) for t in valid_times]
    
    # Find unique years to set the unlimited dimension size
    years = sorted(list(set(d.year for d in dates)))
    num_years = len(years)
    year_map = {y: i for i, y in enumerate(years)}
    
    print(f"Found {num_years} years of data: {years}")

    # Initialize destination arrays with fill values (1.e+30f)
    # Shape: (year, day=366, hour=24, ngrid=1)
    fill_value = 1.e+30
    shape = (num_years, 366, 24, 1)
    
    data_tmph = np.full(shape, fill_value, dtype=np.float32)
    data_windh = np.full(shape, fill_value, dtype=np.float32)
    data_rainh = np.full(shape, fill_value, dtype=np.float32)
    data_dwpth = np.full(shape, fill_value, dtype=np.float32)
    data_sradh = np.full(shape, fill_value, dtype=np.float32)
    data_patm = np.full(shape, fill_value, dtype=np.float32) # Initialize PATM array
    data_years = np.array(years, dtype=np.int32)

    # --- Perform Conversions and Slotting ---
    print("Converting and slotting data...")
    
    for i, dt in enumerate(dates):
        y_idx = year_map[dt.year]
        
        # Day of year (1-366). Python timetuple is 1-366.
        # We need 0-based index for the array (0-365)
        d_idx = dt.timetuple().tm_yday - 1 
        
        # Hour (0-23)
        h_idx = dt.hour
        
        # 1. t2m (K) -> TMPH (C)
        data_tmph[y_idx, d_idx, h_idx, 0] = t2m[i] - 273.15
        
        # 2. u10, v10 (m/s) -> WINDH (m/s)
        wind_speed = np.sqrt(u10[i]**2 + v10[i]**2)
        data_windh[y_idx, d_idx, h_idx, 0] = wind_speed
        
        # 3. tp (m) -> RAINH (mm)
        # ERA5 'tp' is typically accumulated. Assuming hourly steps: m -> mm
        data_rainh[y_idx, d_idx, h_idx, 0] = tp[i] * 1000.0
        
        # 4. d2m (K) -> DWPTH (kPa)
        data_dwpth[y_idx, d_idx, h_idx, 0] = calculate_vapor_pressure(d2m[i])
        
        # 5. ssrd (J/m2) -> SRADH (W/m2)
        # 1 Watt = 1 Joule/second. Hourly accumulation = 3600 seconds.
        # Ensure non-negative radiation
        rad_watts = max(0, ssrd[i] / 3600.0)
        data_sradh[y_idx, d_idx, h_idx, 0] = rad_watts

        # 6. sp (Pa) -> PATM (kPa)
        # 1 kPa = 1000 Pa
        data_patm[y_idx, d_idx, h_idx, 0] = sp[i] / 1000.0

    # --- Write Output File ---
    print(f"Writing output file: {output_filename}")
    dst = nc.Dataset(output_filename, 'w', format='NETCDF4')

    # Dimensions
    dst.createDimension('year', None) # Unlimited
    dst.createDimension('day', 366)
    dst.createDimension('hour', 24)
    dst.createDimension('ngrid', 1)

    # Variables
    # year
    var_year = dst.createVariable('year', 'i4', ('year',))
    var_year.long_name = "year AD"
    var_year[:] = data_years

    # TMPH
    var_tmph = dst.createVariable('TMPH', 'f4', ('year', 'day', 'hour', 'ngrid'), fill_value=fill_value)
    var_tmph.long_name = "hourly air temperature"
    var_tmph.units = "oC"
    var_tmph.missing_value = fill_value
    var_tmph[:] = data_tmph

    # WINDH
    var_windh = dst.createVariable('WINDH', 'f4', ('year', 'day', 'hour', 'ngrid'), fill_value=fill_value)
    var_windh.long_name = "horizontal wind speed"
    var_windh.units = "m s^-1"
    var_windh.missing_value = fill_value
    var_windh[:] = data_windh

    # RAINH
    var_rainh = dst.createVariable('RAINH', 'f4', ('year', 'day', 'hour', 'ngrid'), fill_value=fill_value)
    var_rainh.long_name = "Total precipitation"
    var_rainh.units = "mm m^-2 hr^-1"
    var_rainh.missing_value = fill_value
    var_rainh[:] = data_rainh

    # DWPTH
    var_dwpth = dst.createVariable('DWPTH', 'f4', ('year', 'day', 'hour', 'ngrid'), fill_value=fill_value)
    var_dwpth.long_name = "atmospheric vapor pressure"
    var_dwpth.units = "kPa"
    var_dwpth.missing_value = fill_value
    var_dwpth[:] = data_dwpth

    # SRADH
    var_sradh = dst.createVariable('SRADH', 'f4', ('year', 'day', 'hour', 'ngrid'), fill_value=fill_value)
    var_sradh.long_name = "Incident solar radiation"
    var_sradh.units = "W m^-2"
    var_sradh.missing_value = fill_value
    var_sradh[:] = data_sradh

    # PATM (New Variable)
    var_patm = dst.createVariable('PATM', 'f4', ('year', 'day', 'hour', 'ngrid'), fill_value=fill_value)
    var_patm.long_name = "atmospheric pressure"
    var_patm.units = "kPa"
    var_patm.missing_value = fill_value
    var_patm[:] = data_patm

    # Add other static variables from dry_clm.txt if necessary (Z0G, PHRG, etc)
    # Here we initialize them as fill values or zeros as they aren't in ERA5 source
    
    # Example for Z0G (Wind measurement height - usually 10m for ERA5 u10/v10)
    var_z0g = dst.createVariable('Z0G', 'f4', ('year', 'ngrid'), fill_value=fill_value)
    var_z0g.long_name = "windspeed measurement height"
    var_z0g.units = "m"
    var_z0g[:] = np.full((num_years, 1), 10.0) # ERA5 is 10m wind

    def_vars={'IFLGW':["flag for raising Z0G with vegeation",'','0','i4'],'PHRG':["pH in precipitation",'','7','f4'],
      'CN4RIG':["NH4 conc in precip","gN m^-3",'0','f4'],'CNORIG':["NO3 conc in precip", "gN m^-3",'0','f4'],
    'CPORG':["H2PO4 conc in precip","gP m^-3",'0','f4'],'CALRG':["Al conc in precip","gAl m^-3",'0','f4'],
    'CFERG':["Fe conc in precip","gFe m^-3",'0','f4'],'CCARG':["Ca conc in precip","gCa m^-3",'0','f4'],
    'CMGRG':["Mg conc in precip","gMg m^-3",'0','f4'],'CNARG':["Na conc in precip","gNa m^-3",'0','f4'],
      'CKARG':["K conc in precip","gK m^-3",'0','f4'],'CSORG':["SO4 conc in precip","gS m^-3",'0','f4'],
      'CCLRG':["Cl conc in precip","gCl m^-3",'0','f4']}

    for key,val in def_vars.items():
        var_=dst.createVariable(key,val[-1],('year','ngrid'))
        var_.long_name=val[0]
        var_.units=val[1]
        if val[-1]=='i4':
            var_[:]=int(val[2])
        elif val[-1]=='f4':
            var_[:]=float(val[2])

    var_=dst.createVariable('ZNOONG','f4',('year','ngrid'),fill_value=fill_value)
    var_.long_name='time of solar noon'
    var_.units='hour'
    var_.missing_value = fill_value
    for k in range(num_years):
        date2_year, date2_month, date2_day = years[k], 6, 1
        solar_noon_2 = calculate_solar_noon_utc(date2_year, date2_month, date2_day, lon, lat)
        var_[k]=solar_noon_2

    
    dst.close()
    print("Conversion complete.")

if __name__ == "__main__":
    # Update these filenames as needed
    input_nc = 'reanalysis-era5-single-levels-timeseries-sfcs0p4wh0i.nc' 
    lon,lat=-122.27,37.87
    output_nc = 'berkeley_clm_converted.nc'
    create_clm_file(input_nc, lon, lat, output_nc)