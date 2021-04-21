import http.client
import json
from datetime import date
from datetime import datetime
from datetime import timedelta
import time
import mysql.connector
import os
import numpy as np

#Setting envionrment variables to variables
client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
database_name = os.environ['database_name']
host_name = os.environ['host_name']
password = os.environ['password']
user_name = os.environ['user_name']
redirect_uri = os.environ['redirect_uri']

#########################################################################
#########################################################################
############################### FUNCTIONS ###############################
#########################################################################
#########################################################################

#Used to get an access token just after we have gotten the authorization code from the redirect URI
#This will be used on the initial authorization to get an access token and refresh token
def get_access_and_refresh_tokens(auth_code, client_secret, client_id, redirect_uri):
    conn = http.client.HTTPSConnection("api.dexcom.com")
    payload = "client_secret=" + client_secret + "&client_id=" + client_id + "&code=" + auth_code + "&grant_type=authorization_code&redirect_uri=" + redirect_uri

    headers = {'content-type': "application/x-www-form-urlencoded",'cache-control': "no-cache"}

    conn.request("POST", "/v2/oauth2/token", payload, headers)

    res = conn.getresponse()
    data = res.read()
    #If an invalid authorization code is supplied (e.g, expired) then data will have an error invalid user. This checks the first word to make sure it is not error
    #If it is, the function will return and then try again with a new auth code

    if data[10:23].decode("utf-8") == "invalid_grant":
        return "Error: Invalid Grant", "Error: Invalid Grant"
    else:
        access_token = data[17:1191].decode("utf-8")
        refresh_token = data[1250:1282].decode("utf-8")
        return access_token, refresh_token

#Uses the refresh token we got from above function to get a new access token, this will be used once our access token has expired (7200 seconds, or 2 hours)
def get_new_access_token(refresh_token, client_secret, client_id, redirect_uri):
    print("Old refresh token: " + str(refresh_token))
    conn = http.client.HTTPSConnection("api.dexcom.com")
    payload = "client_secret=" + client_secret + "&client_id=" + client_id + "&refresh_token=" + refresh_token + "&grant_type=refresh_token&redirect_uri=" + redirect_uri

    headers = {'content-type': "application/x-www-form-urlencoded",'cache-control': "no-cache"}

    conn.request("POST", "/v2/oauth2/token", payload, headers)

    res = conn.getresponse()
    data = res.read()
    #print(data.decode("utf-8"))
    print("Obtained new access token")

    #If the refresh_token is invalid (has been used before or has expired) we should get a new one, as well as a new access token. 
    #We will need a new auth_code to get these tokens, this will be handeled in an if statement
    if data[2:7].decode("utf-8") == "error":
        return "Error: Invalid Refresh Token"
    else:
        access_token = data[1041:2217].decode("utf-8")
        return access_token

#Used to make datetime string for making API requests
def time_fn(days, minutesX):
    current_time = datetime.utcnow() - timedelta(days)
    current_timestr = datetime.strftime(current_time, '%Y-%m-%dT%H:%M:%S')
    timestr_minus_5 = current_time - timedelta(minutes = minutesX)
    five_mins_ago_time = datetime.strftime(timestr_minus_5, '%Y-%m-%dT%H:%M:%S')
    url_str = ("startDate=" + str(five_mins_ago_time) + "&" + "endDate=" + str(current_timestr))
    print(url_str)
    return url_str

#Sending API Request with test time
def api_request(access_token, url_string):
    conn = http.client.HTTPSConnection("api.dexcom.com")
    headers = {'authorization': "Bearer " + access_token}

    #Pulling from test time
    conn.request("GET", "/v2/users/self/egvs?" + url_string, headers=headers)

    res = conn.getresponse()
    data = res.read()

    #The function of this if/else is to see if the access token is invalid. If it is, we will generate an error
    if data[25:39].decode("utf-8") == "Invalid Access":
        return "Error: Invalid Access Token"
    else:
        return data

#Turns the JSON data into a dictionary
def data_to_dictionary(data):
    data_dictionary = json.loads(data.decode('utf-8')) #Turns a byte string into a dictionary
    return data_dictionary

def current_utc_time():
    current_utc = datetime.utcnow()
    current_utcstr = datetime.strftime(current_utc, '%Y-%m-%dT%H:%M:%S')
    current_utc_dt = datetime.strptime(current_utcstr, "%Y-%m-%dT%H:%M:%S")
    return current_utc_dt
    
def auc(points):
    for x in range(len(points)):
        points[x] = points[x] - 70
        AUC_Value = abs(np.trapz(points))/10
        if(AUC_Value < 1):
            AUC_Value = 1
        elif(AUC_Value > 10):
            AUC_Value = 10
    return AUC_Value
    
##########################################################################################################################
##########################################################################################################################
############################################# Automatic Data Collection Code #############################################
##########################################################################################################################
##########################################################################################################################
    
def handler(event = None, context = None):
    batch_insert_list = []
    #Establishing a connection to the MySQL database
    error = ""
    error_count = 0

    try:
        db = mysql.connector.connect(
        host= host_name,
        user= user_name,
        passwd= password,
        database= database_name)
    except Exception as e:
        error = str(e)
        print(e)

    #This happens if we lose connection to database
    if(error[0:4] == "2005"):
        error_count += 1
        print("error count: " + str(error_count))
        error = ""

    #If we have no errors
    if(error_count == 0):
        cursor = db.cursor()
        cursor = db.cursor(buffered=True)
        cursor.execute("SELECT * FROM Tokens")
        tokens_values = cursor.fetchall()
        tokens_row = []
        url_string = time_fn(0, 185)
        
    #What each row and column correspond to 
    #User_ID        =   tokens_row[0][0] 
    #Refresh Token  =   tokens_row[0][1]
    #Access Token   =   tokens_row[0][02]
    #Creation_Time  =   tokens_row[0][3]  
        for value in tokens_values:
            tokens_row.append(value)
            #If refresh_token is NULL in database, we skip over this. This means user has yet to authenticate with Dexcom
            if(tokens_row[0][1] is not None):
                #Stores current time into variable in datetime format
                curr_time = datetime.utcnow()
                refresh_token = tokens_row[0][1]
                access_token = tokens_row[0][2]
                #Stores the creation time of access token into this variable
                creation_time = tokens_row[0][3]
                #Gets current user id in current row
                user_id = tokens_row[0][0]

                #If the creation time + 105 mins is less than or equal to the current time, then get new access token
                if(creation_time + timedelta(minutes = 105) <= curr_time):
                    access_token = get_new_access_token(refresh_token, client_secret, client_id, redirect_uri)

                    if(access_token != "Error: Invalid Refresh Token"):
                        #Makes a new creation time for access token
                        new_creation_time = current_utc_time()
                        tokens_update = "UPDATE Tokens SET Access_Token = %s, Creation_Time = %s WHERE User_ID = %s"
                        tokens_values = (access_token, new_creation_time, user_id)
                        try:
                            cursor.execute(tokens_update, tokens_values)
                            db.commit()
                            print("New Access Token and Creation Time Added to Database! At Time: " + str(new_creation_time))
                        except Exception as e:
                            db.rollback()
                            print("Exception Occured: ", e)
                
                #If a new access token is not needed then an api request can be made using the current access token
                else:
                    #API Request and converting the information to dictionary so it's easily storable in variables
                    data = api_request(access_token, url_string)
                    data_dictionary = []
                    if(data == "Error: Invalid Access Token"):
                        pass
                    else:
                        data_dictionary = data_to_dictionary(data)

                    #Storing each piece of data into variable
                    #If the dictionary has something in it, then store that
                    if(len(data_dictionary["egvs"]) > 0):
                        systemTime = datetime.strptime(data_dictionary["egvs"][0]["systemTime"], "%Y-%m-%dT%H:%M:%S")
                        value = data_dictionary["egvs"][0]["value"]
                        trend = data_dictionary["egvs"][0]["trend"]
                        trendRate = data_dictionary["egvs"][0]["trendRate"]
                        batch_insert_list.append((user_id, systemTime, value, trend, trendRate))


            else:
                #User has not authenticated yet, therefore they do not have an access token to be used for an API request
                #we skip over them
                pass

               
            #Clears the list ready for next user
            tokens_row.clear()

        #Inserting into the egvs table the data we just got from api request
        #Inserts each data point into egvs, ignores any errors that would come up like duplicate entry
    egvs_insert = "INSERT IGNORE INTO egvs (UID, systemTime, value, trend, trendRate) VALUES (%s, %s, %s, %s, %s)"
    values = batch_insert_list
    cursor.executemany(egvs_insert, values)
    db.commit()
    print("Successfully Inserted Data")

    ####################################################################################################################################################################################
    ####################################################################################################################################################################################
    ##################################################################################AUC CALCULATION ##################################################################################
    ####################################################################################################################################################################################
    ####################################################################################################################################################################################
    
    #Query that finds all rows without an AUC Value but are ready for AUC calculation (have start and end timestamps)
    cursor.execute("SELECT Usr_ID, Low_Start_Time, Low_End_Time FROM `Dexcom API Info`.AUC WHERE Low_Start_Time IS NOT NULL AND Low_End_Time IS NOT NULL AND AUC_Value IS NULL")

    #Creating a list of tuples of this format: [(Low_Start_Time, Low_End_Time, Usr_ID),.....]
    auc_timestamps = cursor.fetchall()

    #If the list is empty we have no AUC ready for calculation, we do nothing
    if(not auc_timestamps):
        pass

    #Time to calculate some AUC!
    else:
        #Query that will be used in execute in upcoming for loop
        egvs_query = "SELECT value FROM `Dexcom API Info`.egvs WHERE UID = %s AND systemTime >= %s AND systemTime < %s"
        
        #The egvs values will be stored into this list in this format: [[65, 60, 59, 55, 68], [65,...],....]
        values_list = []

        #Going through each of the AUC columns and executing a query to find the low values associated with the timestamps
        for column in range(len(auc_timestamps)):
            cursor.execute(egvs_query, (auc_timestamps[column][0], auc_timestamps[column][1], auc_timestamps[column][2]))
            values_list_of_tuples = cursor.fetchall()
            #Converting a list of tuples [ [(1,), (2,), (3,)], [(4,), (5,), (6,)] to a list of integers -> [[1, 2, 3], [4, 5, 6]] using generator expression
            values_list_of_tuples = [i[0] for i in values_list_of_tuples]
            #Appending the list of integers to the values_list
            values_list.append(values_list_of_tuples)
    
        #Empty list which will be used in next loop to store each AUC value
        AUC_Values = []

        #For each list of egvs values, calculate AUC using that list and append it to the AUC_Values list
        for values in range(len(values_list)):
            AUC_Values.append(auc(values_list[values]))

        #Used in a execute in below for loop in order to UPDATE the AUC table placing the calculated AUC values into the AUC_Value columns
        AUC_update = "UPDATE AUC SET AUC_Value = %s WHERE Usr_ID = %s AND low_start_time = %s"
        for column in range(len(auc_timestamps)):
            try:
                #Update that puts new AUC value into row with speceifc user id and start time (primary key). This works because each list is same length
                cursor.execute(AUC_update, (float(AUC_Values[column]), auc_timestamps[column][0], auc_timestamps[column][1]))
                db.commit()
            except Exception as e:
                db.rollback()
                print("Exception Occured: ", e)
    
    cursor.close()
    db.close()