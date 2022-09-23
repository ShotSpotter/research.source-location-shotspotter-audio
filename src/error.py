"""
DISCLAIMER: This is the locally stored version of the "utm" library found within python's library
            system. They had an issue in their code that didn't properly handle a user externally
            forcing a lat/lon coordinate into a UTM zone that's on the other side of the equator
            than the lat/lon's inherent UTM zone. For instance, given a point in the northern
            hemisphere, the library code before our changes would not properly handle a coercion
            into the southern hemisphere. See LS-1002 (linked below) for a detailed account of the
            changes made.

            The library contained this file (error.py) as well as conversion.py, there is a similar
            disclaimer that count be found there as we needed to store both files locally.

Ticket: https://jira.shotspotter.com/browse/LS-1002
Library repository: https://github.com/Turbo87/utm
Library documentation: https://pypi.org/project/utm/
"""


class OutOfRangeError(ValueError):
    pass
