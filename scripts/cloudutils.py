import os, requests;

def fetch_task_id(
   default_value = "NULL"
):
   
   # Check if running within AWS ECS
   env_aws = os.getenv("ECS_CONTAINER_METADATA_URI_V4");  
   if env_aws is not None:
      
      r = requests.get(env_aws + "/task");
      
      if r.status_code != 200:
        return str(r.status_code);
        
      data = r.json();
      
      if "TaskARN" in data:
         return data["TaskARN"];
         
      else:
         print(str(data));
         return default_value;
   
   # Add additional equivalent checks for other cloud environments
   
   return default_value;


