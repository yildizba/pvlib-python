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

from datetime import timedelta
import pvlib
from pvlib import pvsystem, location, modelchain, iotools
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import pandas as pd
import pathlib
import matplotlib.pyplot as plt
from dataclasses import dataclass

# %%
# First let's grab some weather data and produce a yearly output

EXAMPLE_DEG_PROFILE = [0.0, 0.02, 0.005, 0.005, 0.005]

def apply_simple_degradation(mc, deg_list=EXAMPLE_DEG_PROFILE):
    '''
        Apply a single yearly degradation amount to the total ac output
        of the system.
    '''
    print(mc.results.ac.head())

    year = 0
    year_results = mc.results.ac
    for yearly_deg in deg_list:
        year_results = (1 - yearly_deg) * year_results
        print(year_results[11:16])

    return

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
apply_simple_degradation(mc2)
# results.resample('m').sum().plot()
# plt.ylabel('Monthly Production')
# plt.show()
# plt.savefig('test1.png')

