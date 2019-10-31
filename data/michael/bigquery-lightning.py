# ##############################################################################

import sys, json
from google.cloud import bigquery

# ##############################################################################

# bigquery data source 
source = \
    'bigquery-public-data.noaa_lightning.lightning_2018'

# list of features we want to extract
features = \
    [#'day',
     'number_of_strikes',
     'center_point']


# conjunctive normal from 
#    of condition used to select feature vectors  
conditions = \
    [['TRUE']]

# ##############################################################################

if __name__=="__main__":
    query = f'SELECT day, number_of_strikes, center_point FROM `{source}`'

    cfg = bigquery.QueryJobConfig()
    cfg.dry_run = False
    cfg.maximum_bytes_billed = 200*(10**9); # ~$2
    qstr = query
    
    print('-'*70)
    print(qstr)
    print('-'*70)
    
    cl = bigquery.Client()
    jobq = cl.query(qstr, cfg,
                    location='US')

    print("Gigabytes Processed: {:10.03f}".format(
        (jobq.total_bytes_processed or 0)/10**9))

    assert cfg.dry_run == False

    # Now that we're committed, we'll go ahead and save 
    output = []
    for ii, entry in enumerate(jobq):
        obj = {f: entry[f] for f in features }
        # deal with datetime bullshit
        obj['day'] = f'{entry["day"].year}-{entry["day"].month:02}-{entry["day"].day}'
        
        output.append(obj)
        if ii % 1000 == 0:
            with open('raw-lightening.json', 'a') as out:
                out.write('\n')
                json.dump(output, out)            
            del output
            output = []

            print(f"{ii} ", end='', flush=True)
            pass
        pass
    
    with open('raw-lightening.json', 'a') as out:
        out.write('\n')
        json.dump(output, out)
        pass

