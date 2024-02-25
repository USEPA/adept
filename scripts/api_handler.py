import os,json;
import collections;

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
   if g_config["state_urls"][key]["enabled"]:
      return g_config["state_urls"][key]["url"];

def get_proxy(key):
   if g_config["state_urls"][key]["enabled"]:
      return g_config["state_urls"][key]["proxy"];
 
def update_dict(d,u):
   for k,v in u.items():
      if isinstance(v,collections.abc.Mapping):
         d[k] = update_dict(d.get(k,{}),v);
      else:
         d[k] = v;
   return d;
    
def merge_override(merge_dict):
   global g_config;
   
   if merge_dict is not None: 
      jmerge_dict = json.loads(merge_dict);
      
      g_config = update_dict(g_config,jmerge_dict);

