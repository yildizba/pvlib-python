import logging
pvl_logger = logging.getLogger('pvlib')

import numpy as np


def relativeairmass(z, model='kastenyoung1989'):
    '''
    Gives the relative (not pressure-corrected) airmass

    Gives the airmass at sea-level when given a sun zenith angle, z (in 
    degrees). 
    The "model" variable allows selection of different airmass models
    (described below). "model" must be a valid string. If "model" is not 
    included or is not valid, the default model is 'kastenyoung1989'.

    Parameters
    ----------

    z : float or DataFrame 

      Zenith angle of the sun.  Note that some models use the apparent (refraction corrected)
      zenith angle, and some models use the true (not refraction-corrected)
      zenith angle. See model descriptions to determine which type of zenith
      angle is required.
  
    model : String 
      Avaiable models include the following:

         * 'simple' - secant(apparent zenith angle) - Note that this gives -inf at zenith=90
         * 'kasten1966' - See reference [1] - requires apparent sun zenith
         * 'youngirvine1967' - See reference [2] - requires true sun zenith
         * 'kastenyoung1989' - See reference [3] - requires apparent sun zenith
         * 'gueymard1993' - See reference [4] - requires apparent sun zenith
         * 'young1994' - See reference [5] - requries true sun zenith
         * 'pickering2002' - See reference [6] - requires apparent sun zenith

    Returns
    -------
    AM : float or DataFrame 
            Relative airmass at sea level.  Will return NaN values for all zenith 
            angles greater than 90 degrees.

    References
    ----------

    [1] Fritz Kasten. "A New Table and Approximation Formula for the
    Relative Optical Air Mass". Technical Report 136, Hanover, N.H.: U.S.
    Army Material Command, CRREL.

    [2] A. T. Young and W. M. Irvine, "Multicolor Photoelectric Photometry
    of the Brighter Planets," The Astronomical Journal, vol. 72, 
    pp. 945-950, 1967.

    [3] Fritz Kasten and Andrew Young. "Revised optical air mass tables and
    approximation formula". Applied Optics 28:4735-4738

    [4] C. Gueymard, "Critical analysis and performance assessment of 
    clear sky solar irradiance models using theoretical and measured data,"
    Solar Energy, vol. 51, pp. 121-138, 1993.

    [5] A. T. Young, "AIR-MASS AND REFRACTION," Applied Optics, vol. 33, 
    pp. 1108-1110, Feb 1994.

    [6] Keith A. Pickering. "The Ancient Star Catalog". DIO 12:1, 20,
    
    [7] Matthew J. Reno, Clifford W. Hansen and Joshua S. Stein,
    "Global Horizontal Irradiance Clear Sky Models: Implementation and Analysis"
    Sandia Report, (2012).

    See Also
    --------
    pvl_absoluteairmass
    pvl_ephemeris

    '''
    
    # removed angle check. be responsible. 
    
    model = model.lower()
    
    if 'kastenyoung1989' == model:
        AM = 1.0 / (np.cos(np.radians(z)) + 0.50572*(((6.07995 + (90 - z)) ** - 1.6364)))
    elif 'kasten1966' == model:
        AM = 1.0 / (np.cos(np.radians(z)) + 0.15*((93.885 - z) ** - 1.253))
    elif 'simple' == model:
        AM = np.sec(np.radians(z))
    elif 'pickering2002' == model:
        AM = 1.0 / (np.sin(np.radians(90 - z + 244.0 / (165 + 47.0 * (90 - z) ** 1.1))))
    elif 'youngirvine1967' == model:
        AM = 1.0 / np.cos(np.radians(z))*((1 - 0.0012*((((np.sec(np.radians(z)) ** 2) - 1)))))
    elif 'young1994' == model:
        AM = (1.002432*((np.cos(np.radians(z))) ** 2) + 0.148386*(np.cos(np.radians(z))) + 0.0096467) / (np.cos(np.radians(z)) ** 3 + 0.149864*(np.cos(np.radians(z)) ** 2) + 0.0102963*(np.cos(np.radians(z))) + 0.000303978)
    elif 'gueymard1993' == model:
        AM = 1.0 / (np.cos(np.radians(z)) + 0.00176759*(z)*((94.37515 - z) ** - 1.21563))
    else:
        pvl_logger.warning("{} is not a valid model type for relative airmass. The 'kastenyoung1989' model was used.".format(model))
        AM = 1.0 / (np.cos(np.radians(z)) + 0.50572*(((6.07995 + (90 - z)) ** - 1.6364)))
        
    return AM
