from flask import Flask , render_template , request , abort
import json
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import re 
import requests

client = MongoClient('localhost', 27017)

now = datetime.now()
current_time  = now
# current_time = now.strftime("%d-%m-%Y:%S-%M-%H") #use this to get time 

#db init
db = client.testdb #connecting to the database
collection_users = db.users #connecting to the collection users
collection_rides = db.rides #connecting to the collection users



app = Flask(__name__)

"""

    Note: Whenever there is a read/write/delete operation: just call read() or write() or delete() in the 
    following format :

    READ FORMAT
    >> api_data =
    {
    “table”: “collectionsname”,
    “columns”: [“attributenames",], -------> set this as None if u want all the attributes
    “where”: {"attribute":"value”} ----> set this as None if u want all the rides
    }
    >> read_db(api_data)

    OR

    WRITE FORMAT
    >> api_data = 
    {
    “insert” : <data>,  -----> data will be either a users or rides dictionary with the respective attribute values you want to insert/update
    “table” : “collections_into_which_you_wanna_insert”
    "status" : "delete"/"update"/"insert" -----> depending on whether it is a delete operation or update.
    }
    >> write_db(api_data)

"""

#data structures
#just an instance. this will keep getting overwritten.
users_data = {
    "username" : None ,
    "password" : None,
    "user_status" : None  #valid/invalid 
}

rides_data = {
    "rideId" : None ,#shreya/drasti I need to have a word about this with you
    "created_by" : None,
    "timestamp" : None, #NOT current_time , defined at the top.  
    "source" : None,
    "destination" : None,
    "riders" : [] , #will be a list to which you need to append to.
    "ride_status"  : None #upcomming/completed/deleted
}

def refresh_database():
    #here we just get all the records in the rides db and then update it.
    collection_handler = collection_rides
    data_retrieved  = collection_handler.find({"ride_status":"upcoming"},{"_id":0})
    try:
        for i in data_retrieved:
            temp_time = datetime.strptime(i["timestamp"],r"%d-%m-%Y:%S-%M-%H") 
            if(temp_time < current_time):
                i["ride_status"] = "completed"
                newvalues = { "$set": i }
                collection_handler.update_one({"rideId": i["rideId"]}, newvalues)
    except:
        pass


@app.route("/")
def main():
    return "Wonderful, it works."

# "user" collections functions
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    print("[INFO]:ADD USER FUNCTION EXECUTED")
    refresh_database()
    """ 
    Checks to be made.
    1. Verify the username does not already exist in the existing database. If it does, abort appropriately
    2. If the username does not exist, make sure the SHA in the message body follows the SHA specfications.
    3. If it does, add this user to the the "users" collections.
    """
    try:
        username=request.get_json()["username"]
        password=request.get_json()["password"]
    except:
        #client didn't send stuff properly
        abort(400)
    

    # Verify the username does not already exist in the existing database. If it does, abort appropriately
    api_data = {
    "table": "users",
    "columns": None,
    "where": {"username" : username}
    }
    # data_retrieved = read_db(api_data)
    URL = "http://127.0.0.1:8000/api/v1/db/read"
    data_retrieved = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
    
    if(len(data_retrieved) == 0):
        # If the username does not exist, make sure the SHA in the message body follows the SHA specfications.
        rex=re.compile(r'[0-9a-fA-F]{40}')
        m=rex.search(password)== None 
        if(len(password)==40 and not m):
            # If it does, add this user to the the "users" collections.
            api_data = {
            "insert" : {"username" : username, "password":password, "user_status":"valid"}, 
            "table" : "users",
            "status" : "insert" 
            }

            URL = "http://127.0.0.1:8000/api/v1/db/write"
            requests.post(URL,json=json.dumps(api_data))
            # return "username was added successfully"
            return  {}, 201
        else:
            abort(400)
            # return "password strength inadequate"
            
    else :
        abort(400)
        # return "Username already exists"


@app.route("/api/v1/users/<username>",methods=["DELETE"])
def remove_user(username=None):
    print("[INFO]:REMOVE USER FUNCTION EXECUTED")
    refresh_database()
    """
    1. Check if the user exists. Abort accordingly.
    2. If he does exist, call the write_db() with "username" value set in the user dictionary and status==delete.
    """
    if(username==None):
        #means stuff was not sent properly by the user
        abort(400)
     
    api_data = {
    "table": "users",
    "columns": None,
    "where": {"username" : username}
    }

    
    URL = "http://127.0.0.1:8000/api/v1/db/read"
    data_retrieved = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
    if(len(data_retrieved) == 0):
        abort(400)
        return "username to be deleted does not exists"
    elif(len(data_retrieved) > 1):
        return "probably an error form our side; ignore"
        abort(500)
    else:
        api_data = {
        "insert" : {"username" : username}, 
        "table" : "users",
        "status" : "delete" 
        }
    
    URL = "http://127.0.0.1:8000/api/v1/db/write"
    requests.post(URL,json=json.dumps(api_data))
    return  {}, 200
    """
    1. Check if the user exists. Abort accordingly.
    2. If he does exist, call the write_db() with "username" value set in the user dictionary and status==delete.
    """


# "rides" collections functions
@app.route("/api/v1/rides",methods=["POST"])
def create_ride(): 

    print("[INFO]:CREATE RIDE FUNCTION EXECUTED")
    #refresh database: converting upcoming to completed for rides whose timestamp is less than current timestamp
    refresh_database()

    ##GOING TO ASSUME , SOURCE AND DESTINATION ARE STRING(NUMBERS)
    df = pd.read_csv("AreaNameEnum.csv")
    try:
        data  = request.get_json()
        created_by = request.get_json()["created_by"]
        timestamp = request.get_json()["timestamp"]
        source = request.get_json()["source"]
        destination = request.get_json()["destination"]
    except:
        abort(400)

    if not (re.match("^([0-2][0-9]|(3)[0-1])(-)(((0)[0-9])|((1)[0-2]))(-)\d{4}(:)\d{2}(-)\d{2}(-)\d{2}$",timestamp)):
        abort(400)

    try:
        timestamp_obj = datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H") 
    except:
        abort(400)

    if(timestamp_obj < current_time):
        abort(400)

    #ASSUMING SOURCE AND DESTINATION ARE STRING(INT)
    # #replace source and destination with their respective numbers
    try:
        source_number = df.loc[df["Area No"]==int(source),"Area No"].iloc[0]
        destination_number = df.loc[df["Area No"]==int(destination),"Area No"].iloc[0]
    except:
        abort(400)

    if(source == destination):
        abort(400)

    api_data = {
    "table" : "users",
    "columns": None,
    "where": {"username":created_by} 
    }


    URL = "http://127.0.0.1:8000/api/v1/db/read"
    returned_value = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
    if(len(returned_value)==0):
        #just returning while checking
        abort(400)
        return "username doesn't exist"

    #reading the config file to check which rideId to assign next
    try:
        filee  = open("config.json","r+")
        data_read = json.loads(filee.read())
        data_read["rideId"] = data_read["rideId"] + 1
        filee.seek(0)
        filee.write(json.dumps(data_read))
        filee.truncate()
        filee.close()
    except:
        abort(400)
        return "error opening the configuration file, this message is just for testing purposes"


    rides_data = {
        "rideId" : data_read["rideId"], #this needs to be autoincremented and it will be as it is read from the configuration file
        "created_by" : created_by, #remember to fix 
        
        "timestamp" : timestamp, #defined at the top.  
        "source" : source,
        "destination" : destination,
        "riders" : [created_by] , #will be a list to which you need to append to.
        "ride_status"  : "upcoming"
    }


    api_data = {
        "insert" : rides_data,
        "table" : "rides",
        "status": "insert"
    }

    URL = "http://127.0.0.1:8000/api/v1/db/write"
    requests.post(URL,json=json.dumps(api_data))     


    return  {}, 201

@app.route("/api/v1/rides",methods=["GET"])
def list_allrides():

    print("[INFO]:LIST ALL RIDES FUNCTION EXECUTED")
    try:
        source = request.args.get('source')
        destination =request.args.get('destination')
    except:
        abort(400)


    #refresh database: converting upcoming to completed for rides whose timestamp is less than current timestamp
    refresh_database()

    df = pd.read_csv("AreaNameEnum.csv")

    #ASSUMING SOURCE AND DESTINATION ARE STRING(INT)
    # #replace source and destination with their respective numbers
    try:
        source_number = df.loc[df["Area No"]==int(source),"Area No"].iloc[0]
        destination_number = df.loc[df["Area No"]==int(destination),"Area No"].iloc[0]
    except:
        # return "WRONG ADDRESS"
        abort(400)

    api_data = {
        "table": "rides",
        "columns": None,
        "where": { "source" : source,
                   "destination" : destination
                 }
    }

    
    URL = "http://127.0.0.1:8000/api/v1/db/read"
    data_retrieved = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
    for i in data_retrieved:
        i.pop("ride_status") #we do not need to display that
        i.pop("source")
        i.pop("destination")
        i.pop("riders")
        i["username"] = i.pop("created_by")
    
    
    cpy_data = list(data_retrieved)
    if(len(cpy_data)==0):
        return "",204
    else:
        return json.dumps(data_retrieved),200



@app.route("/api/v1/rides/<int:rideId>",methods=["GET"])
def list_specefic(rideId=None):

    print("[INFO]:LIST SPECIFIC RIDE FUNCTION EXECUTED")
    #refresh database: converting upcoming to completed for rides whose timestamp is less than current timestamp
    refresh_database()

    if(rideId==None):
        abort(400) #means data was not sent properly

    #assuming an alpha-numeric rideId, hence string
    api_data = {
        "table": "rides",
        "columns": None,
        "where": {"rideId" : rideId}
    }

    URL = "http://127.0.0.1:8000/api/v1/db/read"
    data_retrieved = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
    if(len(data_retrieved)==0):
        abort(400)
        return "rideId doesn't exist"



    cpy_data = list(data_retrieved) #hopefully this list conversion workds properly
    if(len(cpy_data)==0):
        return "",204
    else:
        return json.dumps(data_retrieved[0]),200 #of the form {} ; returning just the 0th element as that will be the only dictionary


@app.route("/api/v1/rides/<int:rideId>",methods=["POST"])
def join_existing(rideId=None):
    print("[INFO]:JOIN EXISTING RIDE FUNCTION EXECUTED")
    if(rideId==None):
        abort(400)
    try:
        username = request.get_json()["username"]
    except:
        abort(400)

    refresh_database()

    #first we need to check if this username is a valid username or not
    api_data = {
    "table": "users",
    "columns": None,
    "where": {"username" : username}
    }
    
    URL = "http://127.0.0.1:8000/api/v1/db/read"
    data_retrieved = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
    if(len(data_retrieved)==0):
        abort(400)
        return "username doesn't exist"


    """uncomment the following lines at the end"""
    # elif(len(data_retrieved)>1):
        #possibly some kind of data corruption in the users collection
        #uncomment it all at the end
        # abort(500)


    
    #now we need to check if the rideId exists
    api_data = {
    "table": "rides",
    "columns": None,
    "where": {"rideId" : rideId}
    }

    URL = "http://127.0.0.1:8000/api/v1/db/read"
    data_retrieved = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
    if(len(data_retrieved)==0):
        abort(400)
        return "rideId doesn't exist"


    #assuming all the checks are done and everyhting is valid, lets proceed with the update

    api_data = {
    "insert" : {"rideId" : rideId, "riders":username}, #rideId cannot be updated, but will be used to find that specefic document
    "table" : "rides",
    "status" : "update" 
    }
    
    URL = "http://127.0.0.1:8000/api/v1/db/write"
    requests.post(URL,json=json.dumps(api_data))
    return  {},200



@app.route("/api/v1/rides/<int:rideId>",methods=["DELETE"])
def delete_ride(rideId=None):
    print("[INFO]:DELETE RIDE FUNCTION EXECUTED")
    if(rideId==None):
        abort(400)
    
    refresh_database()
    
    #now we need to check if the rideId exists
    api_data = {
    "table": "rides",
    "columns": None,
    "where": {"rideId" : rideId}
    }
    URL = "http://127.0.0.1:8000/api/v1/db/read"
    data_retrieved = json.loads(requests.post(URL,json=json.dumps(api_data)).content)

    if(len(data_retrieved)==0):
        # return "rideId doesn't exist"
        abort(400)

    
    api_data = {
    "insert" : {"rideId" : rideId}, #rideId will be used to delete that document
    "table" : "rides",
    "status" : "delete" 
    }
    
    URL = "http://127.0.0.1:8000/api/v1/db/write"
    requests.post(URL,json=json.dumps(api_data))
    # return "deletion done"
    # if(write_db(api_data)):
    return  {},200


"""
NOte:

1.Ishwar will code the read_db and write_db functions. Just pick a function, discuss on the group
and code your part. Call the read_db and write_db functions properly.

2.read_db() will always return a list of user/rides dictionaries. It can be a single mongoDB document in the form
[{}] or many matching documents of the form [{},{},{},{}]

3. Do not fuck up the write operations. Set the _status variables properly.

4. Return the dictionaries properly from your functions. call
>> return json.dumps(your_return_dictionary)

5. Don't be a dumbass by sharing this template with others. #obviously

6. Write proper comments. 

"""
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
    print("[INFO]:READ DB FUNCTION EXECUTED")
    refresh_database()
    """
    READ FORMAT
    >> api_data =
    {
    “table”: “collectionsname”,
    “columns”: [“attributenames",], -------> set this as None if u want all the attributes
    “where”: {"attribute"="value”} ----> set this as None if u want all the rides
    }
    so this is the incomming data ; for now let's just code assuming columns=None and we return all values
    """
    try:
        dictionary_data = {}
        print("IN THE READ DB FUNCTION",request.get_json())
        dictionary_data["table"] = json.loads(request.get_json())["table"]
        print( dictionary_data["table"])
        dictionary_data["columns"] = json.loads(request.get_json())["columns"]
        print( dictionary_data["columns"])
        dictionary_data["where"] = json.loads(request.get_json())["where"]
        print( dictionary_data["where"])

    except:
        return "some error in readdb json data"
        pass

    #first we need to figure out which collection we need to append to
    #defining a collection handler
    if(dictionary_data["table"]=="users"):
        collection_handler = collection_users
        doc = "user_status"
        document_status = "valid"
    elif(dictionary_data["table"]=="rides"):
        collection_handler = collection_rides
        doc = "ride_status"
        document_status = "upcoming"
    print("COMES HERE!")
    # if(dictionary_data["columns"]==None): #getting all the attributes
    print("CONSTRAINT CHECKING",dictionary_data["where"])
    print("-----------\n")
    dictionary_data["where"][doc]= document_status
    print("WHERE STATUS",dictionary_data["where"])
    data_retrieved  = collection_handler.find(dictionary_data["where"],{"_id":0}) 
    return json.dumps(list(data_retrieved)) # [{}] format


@app.route("/api/v1/db/write",methods=["POST"])
def write_db():
    print("[INFO]:WRITE DB FUNCTION EXECUTED")
    refresh_database()
    """
    recieved
    api_data = {
            "insert" : rides_data,
            "table" : "rides",
            "status": "insert"
        } incomming data format , where rides_data is the record we need to insert
    """
    #first we need to figure out which collection we need to append to
    #defining a collection handler
    try:
        dictionary_data = {}
        print("IN THE READ DB FUNCTION",request.get_json())
        dictionary_data["insert"] = json.loads(request.get_json())["insert"]
        print( dictionary_data["insert"])
        dictionary_data["table"] = json.loads(request.get_json())["table"]
        print( dictionary_data["table"])
        dictionary_data["status"] = json.loads(request.get_json())["status"]
        print( dictionary_data["status"])

    except:
        return "some error in readdb json data"
        pass

    if(dictionary_data["table"]=="users"):
        collection_handler = collection_users
    elif(dictionary_data["table"]=="rides"):
        collection_handler = collection_rides
  
    #now we need to check the status and see what kind of write is being requested for
    write_type = dictionary_data["status"]

    if write_type == "insert":
        collection_handler.insert_one(dictionary_data["insert"]) 

    elif write_type == "update":
        temp = dictionary_data["insert"]   #{"rideId" : rideId, "riders":username}
        print("PRINTTING TEMPORARY")
        print(temp)
        print("\n -----------")
        myquery = {"rideId": temp["rideId"]}
        #using my query, lets first get the record of that particular rideId
        #we need to set api_data again
        api_data = {
        "table": "rides",
        "columns": None,
        "where": {"rideId": temp["rideId"]}
         }

        URL = "http://127.0.0.1:8000/api/v1/db/read"
        retrieved_record = json.loads(requests.post(URL,json=json.dumps(api_data)).content)

        print("DATA RETRIVED WAS",retrieved_record)
        if(len(retrieved_record)!=1):
            print("into the update 500 error")
            abort(500)
        else:
            retrieved_record = retrieved_record[0] #coz the return is in the form of a list
            #now lets update this retrieved record with the new values
            for key in temp.keys():
                if(key!="rideId" and key!="riders"):
                    retrieved_record[key]=temp[key] #replacing all the old values with the new values #need a for loop to replace every key value pair
                elif(key=="riders"):
                    retrieved_record[key].append(temp[key])
                    retrieved_record[key] = list(set(retrieved_record[key]))
            #once this is done, we need to write "retireved_record" back into the mongo db     
            newvalues = { "$set": retrieved_record }
            collection_handler.update_one(myquery, newvalues) #find the document with myquery and update it with the newvalues

    elif write_type == "delete":
        #here we need to find that particular record and not delete it, but just set the rides status or the user status to deleted/invalid
        if(dictionary_data["table"]=="users"):
            document_status = "invlaid"
            set_table = "users"
        else: #if it is rides
            document_status = "deleted"
            set_table = "rides"

        temp = dictionary_data["insert"]   #{"rideId" : rideId} or ("username":username)
        myquery = temp 
        """{"rideId": temp["rideId"]} #same thing. didn't bother removing the variable
        using my query, lets first get the record of that particular rideId
        we need to set api_data again"""

        api_data = {
        "table":set_table,
        "columns": None,
        "where": temp
        }
        print("IN THE DELETE",api_data)
        URL = "http://127.0.0.1:8000/api/v1/db/read"
        retrieved_record = json.loads(requests.post(URL,json=json.dumps(api_data)).content)
       
        if(len(retrieved_record)!=1):
            abort(500)
        else:
            retrieved_record = retrieved_record[0] #coz the return is in the form of a list
            #now lets update this retrieved record with the new values 
            print("CHECKING THE RETRIEVED IN DELETE",retrieved_record)
            newvalues = { "$set": {set_table[:-1]+"_status" : document_status }} #set_table[-1] = ride/user + "_status"
            collection_handler.update_one(myquery, newvalues) #find the document with myquery and update it with the newvalues
                
    return True


