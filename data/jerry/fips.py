def FIPS_finder():
    import pandas as pd

    df_FIPS = pd.read_csv("https://raw.github.com/differentiablef/map-viz-project/master/data/jerry/statecounty.csv")
	
    def county_FIPS(istate, icounty):
        if not isinstance(istate, int):
            return None
        if not isinstance(icounty, int):
            return None
        
        xx = df_FIPS.loc[(df_FIPS['statecode'].astype(int)==istate) & (df_FIPS['countycode'].astype(int)==icounty)]
        if len(xx) > 0:
            return xx.iloc[0,3]
        else:
            return None
        
        
    def county_code_FIPS(state_str, county_str):
        # Returns the FIPS code of a county.
        if not isinstance(state_str, str):
            return None
        if not isinstance(county_str, str):
            return None
        
        xx = df_FIPS.loc[(df_FIPS['state']==state_str) & (df_FIPS['county']==county_str)]
        if len(xx) > 0:
            return xx.iloc[0,0], xx.iloc[0,1] 
        else:
            return None
        
    return county_FIPS, county_code_FIPS