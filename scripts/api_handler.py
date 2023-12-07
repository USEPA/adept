state_urls = [
                {'AK': 'https://dec.alaska.gov/dww/'},
                {'AL': 'http://dww.adem.alabama.gov/DWW/'},
                {'AZ': 'https://azsdwis.azdeq.gov/DWW_EXT/'},
                {'CA': 'https://sdwis.waterboards.ca.gov/PDWW/'},
                {'DE': 'https://drinkingwater.dhss.delaware.gov/'},
                {'GA': 'https://gadrinkingwater.net/DWWPUB/'},
                {'IA': 'http://programs.iowadnr.gov/drinkingwaterwatch/'},
                {'ID': 'http://dww.deq.idaho.gov/IDPDWW/'},
                {'IL': 'https://water.epa.state.il.us/dww/'},
                # {'KS': 'https://dww.kdhe.ks.gov/DWW/JSP/SearchDispatch'},
                {'KY': 'https://dep.gateway.ky.gov/DWW/'},
                {'MD': 'https://mdesdwis.mde.state.md.us/DWW/'},
                {'MO': 'https://www.dnr.mo.gov/DWW/'},
                {'MS': 'https://apps.msdh.ms.gov/DWW/'},
                {'MT': 'https://sdwisdww.mt.gov/DWW/'},
                {'NC': 'https://www.pwss.enr.state.nc.us/NCDWW2/'},
                {'NE': 'https://drinkingwater.ne.gov/'},
                {'NM': 'https://dww.water.net.env.nm.gov/NMDWW/'},
                {'NV': 'https://ndwis.ndep.nv.gov/DWW/'},
                {'OH': 'https://dww.epa.ohio.gov/DWW/'},
                {'OK': 'http://sdwis.deq.state.ok.us/DWW/'},
                {'RI': 'https://dwq.health.ri.gov/DWW/'},
                {'SC': 'http://dwwwebvm.dhec.sc.gov:8080/DWW/'},
                {'TX': 'https://dww2.tceq.texas.gov/DWW/'},
                {'VT': 'https://anrnode.anr.state.vt.us/DWW/'},
                {'WV': 'https://dww.wvdhhr.org/DWWpublic/'},
                {'WY': 'https://sdwisdww.epa.gov/DWWR8WY/'},
                {'R8': 'https://sdwisdww.epa.gov/DWWR8WY/'},
              ]   

csrf_token_states = ['KS','MO','RI']

texas_like_states = ['TX','NM','NC','KS','MO','RI']

nondrilldown_reports = ['Buyers of Water', 'Chemical Sample Schedules']

noscrape_nav_reports = ['index', 
                        'AllTemplates',
                        'AnalyteList', 
                        'AnalyteListByCode', 
                        'Map_Template',
                        'NMonitoringResultsByAnalyte',
                        'CCR'
                        ]

def get_url(key):
    return [d[key] for d in state_urls if key in d][0]
    