"""SEC state and Canadian province codes for company/filing queries."""

from enum import Enum


class StateCodes(Enum):
    """Represents all the State Codes that can be used to query
    both company and filing information.

    ### Usage
    ----
        >>> from edgar.enums import StateCodes
        >>> StateCodes.TEXAS.value
    """

    ALABAMA = 'AL'
    ALASKA = 'AK'
    ARIZONA = 'AZ'
    ARKANSAS = 'AR'
    CALIFORNIA = 'CA'
    COLORADO = 'CO'
    CONNECTICUT = 'CT'
    DELAWARE = 'DE'
    DISTRICT_OF_COLUMBIA = 'DC'
    FLORIDA = 'FL'
    GEORGIA = 'GA'
    HAWAII = 'HI'
    IDAHO = 'ID'
    ILLINOIS = 'IL'
    INDIANA = 'IN'
    IOWA = 'IA'
    KANSAS = 'KS'
    KENTUCKY = 'KY'
    LOUISIANA = 'LA'
    MAINE = 'ME'
    MARYLAND = 'MD'
    MASSACHUSETTS = 'MA'
    MICHIGAN = 'MI'
    MINNESOTA = 'MN'
    MISSISSIPPI = 'MS'
    MISSOURI = 'MO'
    MONTANA = 'MT'
    NEBRASKA = 'NE'
    NEVADA = 'NV'
    NEW_HAMPSHIRE = 'NH'
    NEW_JERSEY = 'NJ'
    NEW_MEXICO = 'NM'
    NEW_YORK = 'NY'
    NORTH_CAROLINA = 'NC'
    NORTH_DAKOTA = 'ND'
    OHIO = 'OH'
    OKLAHOMA = 'OK'
    OREGON = 'OR'
    PENNSYLVANIA = 'PA'
    RHODE_ISLAND = 'RI'
    SOUTH_CAROLINA = 'SC'
    SOUTH_DAKOTA = 'SD'
    TENNESSEE = 'TN'
    TEXAS = 'TX'
    UNITED_STATES = 'X1'
    UTAH = 'UT'
    VERMONT = 'VT'
    VIRGINIA = 'VA'
    WASHINGTON = 'WA'
    WEST_VIRGINIA = 'WV'
    WISCONSIN = 'WI'
    WYOMING = 'WY'
    ALBERTA_CANADA = 'A0'
    BRITISH_COLUMBIA_CANADA = 'A1'
    MANITOBA_CANADA = 'A2'
    NEW_BRUNSWICK_CANADA = 'A3'
    NEWFOUNDLAND_CANADA = 'A4'
    NOVA_SCOTIA_CANADA = 'A5'
    ONTARIO_CANADA = 'A6'
    PRINCE_EDWARD_ISLAND_CANADA = 'A7'
    QUEBEC_CANADA = 'A8'
    SASKATCHEWAN_CANADA = 'A9'
    YUKON_CANADA = 'B0'
