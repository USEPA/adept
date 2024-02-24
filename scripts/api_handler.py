import os,json;

# Import the configuration to a global
f = open(
   os.path.join(
       os.path.realpath(
         os.path.join(os.getcwd(),os.path.dirname(__file__))
       )
      ,'config.json'
   )
); 
g_config = json.load(f);

csrf_token_states = ['KS','MO','RI']

texas_like_states = ['TX','NM','NC','KS','MO','RI']

nondrilldown_reports = ['Buyers of Water', 'Chemical Sample Schedules']

noscrape_nav_reports = ['index', 
                        'AllTemplates',
                        'AnalyteList', 
                        'AnalyteListByCode', 
                        'Map_Template',
                        'NMonitoringResultsByAnalyte',
                        'CCR',
                        'PosTcrSampleResults'
                        ]

def state_urls():
   state_urls = [];
   for key,val in g_config["state_urls"].items():
      if val["enabled"]:
         state_urls.append({
            key: val['url']
         });
         
   return state_urls;

def get_url(key):
   return [d[key] for d in state_urls() if key in d][0]
 
def merge_override(merge_dict):
   g_config = g_config ** merge_dict;
   