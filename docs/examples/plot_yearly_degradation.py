"""
Yearly Degradation
=============

Example of applying yearly degradation to an output.
"""

# %%
# To generate a lifetime output of a solar system,
# the changes in yearly efficeincy need to be considered.
# This example shows how to apply yearly degradation to 
# any pvlib output.

from datetime import datetime, timedelta
import pvlib
from pvlib import pvsystem, location, modelchain, iotools
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import pandas as pd
import pathlib
import matplotlib.pyplot as plt
from dataclasses import dataclass


EXAMPLE_DEG_PROFILE = [0.0, 0.02, 0.005, 0.005, 0.005]
EXAMPLE_MODULE_DEG = pd.DataFrame({
    'pdc0': EXAMPLE_DEG_PROFILE,
    'gamma_pdc': EXAMPLE_DEG_PROFILE,
    'b': EXAMPLE_DEG_PROFILE,
})

def apply_simple_degradation(mc, deg_list=EXAMPLE_DEG_PROFILE):
    '''
        Apply a single yearly degradation amount to the total ac output
        of the system.
    '''
    
    year_results = mc.results.ac
    degraded_output = pd.Series()

    for yearly_deg in deg_list:
        # apply % degradation
        year_results = (1 - yearly_deg) * year_results

        # save the yearly output to the degraded output series
        degraded_output = degraded_output.append(year_results)

        # Go to next year
        year_results.index = year_results.index.map(
            lambda t: t.replace(year=t.year+1)
        )

    return degraded_output

def apply_module_param_degradation(mc, weather, deg_df=EXAMPLE_MODULE_DEG):
    '''
        Apply yearly degradation to module parameters to get the output
        over the system lifetime
    '''

    # get the existing module parameters from the model chain
    module_params = mc.system.arrays[0].module_parameters
    module_params_deg = module_params

    # set the output series, the start year and degradation list
    degraded_output = pd.Series()
    year = weather.index[0].year
    deg_list = deg_df.to_dict('records')

    # run through all the years of degradation params
    for deg_params in deg_list:

        # set the module params for the next year, checking if each value
        # given in degradation is in the moduel params
        for param, val in deg_params.items():
            if param in module_params_deg:
                module_params_deg[param] = module_params_deg[param] * (1 - val)
            else:
                print(
                    ("Module parameter, {0}, not in current module parameters. " +
                    "Please use one of {1} instead").\
                    format(param, module_params_deg.keys()))
                print(str(module_params_deg.keys()))

        # set the new parameters and run the model
        mc.system.arrays[0].module_parameters = module_params_deg
        _ = mc.run_model(weather)
        year_results = mc.results.ac

        # append the result to the degraded output, with correct year
        year_results.index = year_results.index.map(
            lambda t: t.replace(year=year)
        )
        degraded_output = degraded_output.append(year_results)

        year += 1

    return degraded_output
    

# %%
# First let's grab some weather data and produce a yearly output
DATA_DIR = pathlib.Path(pvlib.__file__).parent / 'data'
tmy, metadata = iotools.read_tmy3(DATA_DIR / '723170TYA.CSV', coerce_year=1990)
# shift from TMY3 right-labeled index to left-labeled index:
tmy.index = tmy.index - pd.Timedelta(hours=1)
weather = pd.DataFrame({
    'ghi': tmy['GHI'], 'dhi': tmy['DHI'], 'dni': tmy['DNI'],
    'temp_air': tmy['DryBulb'], 'wind_speed': tmy['Wspd'],
})
loc = location.Location.from_tmy(metadata)

module_parameters = {'pdc0': 1, 'gamma_pdc': -0.004, 'b': 0.05}
temp_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']

array2 = pvsystem.Array(mount=pvsystem.FixedMount(30, 180),
                        module_parameters=module_parameters,
                        temperature_model_parameters=temp_params)
system2 = pvsystem.PVSystem(arrays=[array2], inverter_parameters={'pdc0': 1})
mc2 = modelchain.ModelChain(system2, loc, spectral_model='no_loss')
_ = mc2.run_model(weather)

# %%
# Plotting the yearly output we can see

# sphinx_gallery_thumbnail_number = 2
results = pd.DataFrame({
    'Year 1 Output': mc2.results.ac,
})
# degraded_output = apply_simple_degradation(mc2)
degraded_output = apply_module_param_degradation(mc2, weather)

yearly_output = pd.DataFrame(degraded_output)
yearly_output.columns = ['ac_output']
yearly_output['year'] = yearly_output.index.year
yearly_output['datetime'] = yearly_output.index.map(
    lambda t: t.replace(year=2000)
)
yearly_output = yearly_output.pivot(index='datetime', columns='year')
print(yearly_output.sum())
yearly_output.resample('m').sum().plot()
plt.ylabel('Monthly Production')
plt.show()
plt.savefig('test1.png')

