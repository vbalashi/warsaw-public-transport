# Coordinates of stops
DB API allows you to access resources stored in databases. DB API provides the following methods:
DB API resource download

https://api.um.warszawa.pl/api/action/dbstore_get
Example call
https://api.um.warszawa.pl/api/action/dbstore_get?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&apikey=wartość
Example call (with page and size parameters)
https://api.um.warszawa.pl/api/action/dbstore_get?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&page=1&size=5&apikey=wartość
Example call (with sortBy)
https://api.um.warszawa.pl/api/action/dbstore_get?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&sortBy=id&apikey=wartość

ab75c33d-3a26-4342-b36a-6e5fef0a3ac3

# Coordinates of stops for the current day
DB API resource download

https://api.um.warszawa.pl/api/action/dbstore_get
Example call
https://api.um.warszawa.pl/api/action/dbstore_get?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey=wartość
Example call (with page and size parameters)
https://api.um.warszawa.pl/api/action/dbstore_get?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&page=1&size=5&apikey=wartość
Example call (with sortBy)
https://api.um.warszawa.pl/api/action/dbstore_get?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&sortBy=id&apikey=wartość

1c08a38c-ae09-46d2-8926-4f9d25cb0630

# Access to ZTM timetables via API

DBtimetable API allows access to public transport timetables. It provides the following methods:

DBtimatable API function call	https://api.um.warszawa.pl/api/action/dbtimetable_get

Example calls - downloading a set of stops
https://api.um.warszawa.pl/api/action/dbtimetable_get?id=b27f4c17-5c50-4a5b-89dd-236b282bc499&name=nazwaprzystanku&apikey=wartość

b27f4c17-5c50-4a5b-89dd-236b282bc499

Example call - downloading lines available at a stop
https://api.um.warszawa.pl/api/action/dbtimetable_get?id=88cd555f-6f31-43ca-9de4-66c479ad5942&busstopId=wartość&busstopNr=wartość&apikey=wartość

88cd555f-6f31-43ca-9de4-66c479ad5942

Example call - downloading the timetable for a line
https://api.um.warszawa.pl/api/action/dbtimetable_get?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238&busstopId=wartość&busstopNr=wartość&line=wartość&apikey=wartość

e923fa0e-d96c-43f9-ae6e-60518c9f3238

DBtimetable API allows access to public transport timetables. It provides the following methods:

DBtimatable API function call	https://api.um.warszawa.pl/api/action/dbtimetable_get



# Description of CKAN API
Data can be accessed via API using the following actions
Query
https://api.um.warszawa.pl/api/action/datastore_search
Sample query (returns the first 5 results)
https://api.um.warszawa.pl/api/action/datastore_search?resource_id=20d30ed7-fa28-478b-b2e3-17e4a5315e71&limit=5
Example query (returns results containing 'jones')
https://api.um.warszawa.pl/api/action/datastore_search?resource_id=20d30ed7-fa28-478b-b2e3-17e4a5315e71&q=jones



Example: Python »

      import urllib
      url = 'https://api.um.warszawa.pl/api/action/datastore_search?resource_id=20d30ed7-fa28-478b-b2e3-17e4a5315e71&limit=5'  
      fileobj = urllib.urlopen(url)
      print fileobj.read()



busstopId = значение из zespol
busstopNr = значение из slupek



