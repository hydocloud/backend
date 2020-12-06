# Users

Database: users
Tables: ```user_group```, ```user_belong_user_groups```

## API:

**Database**: ```user_group```  

POST: create user group 
DELETE: delete user group   
PUT: edit user group        
GET: get all user groups filter by organization id  
GET/{id}: get user group by id     

**Database**: ```user_belong_user_groups```     

POST: add user to user group    
DELETE: delete user from user group     
PUT: edit user group attributes     
GET: get all user groups with all organizations.    
GET/{id}: get attributes for user groups    