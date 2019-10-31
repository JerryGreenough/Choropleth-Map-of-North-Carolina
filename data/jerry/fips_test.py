from fips import FIPS_finder
county, county_code = FIPS_finder()

print(county(37, 119))
print(county_code('LA', 'Jefferson Parish'))