import mysql.connector
import pandas as pd
import numpy as np
import math

from pymongo import  MongoClient

import cosine_similarity as cs

import configparser
config = configparser.ConfigParser()
config.read('briqApp_Config.ini')


def helloWorld():
    return "Hello World"


def checkForConnectionToMySQL():
    """ Connect to MySQL database """
    conn = None
    returnValue = False
    try:
        conn = mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])
        if conn.is_connected():
            print('MySQL database connection check - verified')
            returnValue = True
    except Exception as e:
        print('MySQL database connection check - Could not be established \n {} '.format(e))
        returnValue = False
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
        
    return returnValue

def checkForTable():
    """ Connect to MySQL Table """
    conn = None
    returnValue = False
    try:
        conn = mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])
        cursor = conn.cursor()
        
        # Drop table if it already exist using execute() method.
        sql_drop = "DROP TABLE IF EXISTS quote"
        cursor.execute(sql_drop)
        
        # Create table as per requirement
        sql = """
            create table quote(    
                quote_id INT NOT NULL AUTO_INCREMENT,    
                id VARCHAR(50) NOT NULL,    
                quotes VARCHAR(1000) NOT NULL,    
                author VARCHAR(40),    
                source VARCHAR(500),    
                rating INT,     
                addedBy VARCHAR(40) NOT NULL,    
                delete_flag boolean DEFAULT False,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                modified_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY ( quote_id )
            );"""
        
        cursor.execute(sql)

        conn.commit()
        conn.close()
        returnValue = True
        print('MySQL Table Check - Verified')

    except Exception as e:
        print('MySQL Table Check - Table Not Found \n {} '.format(e))
        returnValue = False
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
        
    return returnValue


def checkNaNReturnNone(valueCheck):
    try:
        if (str(type(valueCheck)) == "<class 'float'>" ):
            if math.isnan(valueCheck) :
                return None
            else: 
                return valueCheck
        else:
            return valueCheck
    except Exception as e: 
        print(e)
        return None

def getDBConnection():
    return mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])

def getMongoDBConnection():
    return MongoClient(config['mongo_database']['host'], config['mongo_database']['port'])

def ImportAllDataFromExcelToMySQL():
    df = pd.read_excel(config['excel_file']['excelFileName'], sheet_name=config['excel_file']['sheetName'])

    sql_insert_query = """ INSERT INTO quote (id, quotes, author, source, rating, addedBy) VALUES (%s,%s,%s,%s, %s, %s)"""
    conn = mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])
    cursor = conn.cursor()


    for row in df.to_dict('records'): 
        try:
            valueId = checkNaNReturnNone(row["id"])
            valueQuotes = checkNaNReturnNone(row["quotes"])
            valueAuthor =  checkNaNReturnNone(row["author"])
            valueSource = checkNaNReturnNone(row["source"])
            valueRating = checkNaNReturnNone(row["rating"])
            valueAddedBy = checkNaNReturnNone(row["addedBy"])
            
            cursor.execute(sql_insert_query, (valueId,  valueQuotes, valueAuthor ,  valueSource,  valueRating, valueAddedBy))           
        except Exception as e: 
            print(e)
            print((row["id"],  row["quotes"], row["author"] ,  row["source"],  row["rating"], row["addedBy"]))

    conn.commit()
    conn.close()
    
    # pushing to mongodb
    pushDataToMongo(df)

def getAllQuote(objectQuote):
    conn = None
    records = None
    try:
        conn = mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])
        cursor = conn.cursor()

        select_query = """SELECT * from {} where delete_flag = {}""".format(config['msql_database']['table'], False)
        cursor.execute(select_query)
        columns = cursor.description 
        records = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()

    except Exception as err:
        print("Failed to read data from table", err)
    finally:
        if (conn):
            conn.close()
    return records

def getSingleQuote(objectQuote):
    conn = None
    record = None
    try:
        conn = mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])
        cursor = conn.cursor()

        select_query = """SELECT * from {} where delete_flag = {} and quote_id = {} """.format(config['msql_database']['table'], False, returnValidInput(objectQuote, "quote_id"))
        cursor.execute(select_query)
        columns = cursor.description
        record = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
    except Exception as err:
        print("Failed to fetch data from table", err)
    finally:
        if (conn):
            conn.close()
    return record

def returnValidInput(objectQuote, propString):
    if propString in objectQuote:
        return objectQuote[propString]
    return None

def insertQuote(objectQuote):
    conn = None
    returnValue = False
    try:
        sql_insert_query = """ INSERT INTO quote (id, quotes, author, source, rating, addedBy) VALUES (%s,%s,%s,%s, %s, %s)"""
        conn = getDBConnection()
        cursor = conn.cursor()
        
        valueId = returnValidInput(objectQuote, "id")
        valueQuotes = returnValidInput(objectQuote, "quotes")
        valueAuthor = returnValidInput(objectQuote, "author")
        valueSource = returnValidInput(objectQuote, "source")
        valueRating = returnValidInput(objectQuote, "rating")
        valueAddedBy = returnValidInput(objectQuote, "addedBy")
            
        cursor.execute(sql_insert_query, (valueId,  valueQuotes, valueAuthor ,  valueSource,  valueRating, valueAddedBy))           
        conn.commit()

        returnValue = True
    except Exception as e: 
        print(e)
        returnValue = False
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
    
    return returnValue


def updateQuote(objectQuote):
    conn = None
    returnValue = False
    try:
        sql_insert_query = "UPDATE {} SET rating = %s, modified_on={} WHERE quote_id = %s".format(config['msql_database']['table'], 'CURRENT_TIMESTAMP')
        conn = getDBConnection()
        cursor = conn.cursor()
        
        val = ( returnValidInput(objectQuote, "rating"), returnValidInput(objectQuote, "quote_id"))

        cursor.execute(sql_insert_query, val)

        conn.commit()

        if returnValidInput(objectQuote, "rating") > 3 :
            pushSinqleQuoteToMongo(getSingleQuote( { "quote_id":returnValidInput(objectQuote, "rating") }))

        returnValue = True
    except Exception as e: 
        print(e)
        returnValue = False
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
    
    return returnValue

def pushSinqleQuoteToMongo(singleQuoteObject):
    try:
        connection = getMongoDBConnection()
        my_database = connection.briqApp
        data = my_database.quote
        
        data.insert( singleQuoteObject )
    except:
        print("Unable to connect to Mongo Database")

def getRatedQuotesByUser(objectQuote):
    conn = None
    records = None
    try:
        conn = mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])
        cursor = conn.cursor()

        select_query = """SELECT * from {} where rating is not Null and delete_flag = False and addedBy = %s""".format(config['msql_database']['table'])
        print(select_query)
        cursor.execute(select_query, (objectQuote["addedBy"],))
        columns = cursor.description 
        records = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()

    except Exception as err:
        print("Failed to read data from table", err)
    finally:
        if (conn):
            conn.close()
    return records

# Hard Delete
def removeQuotes(objectQuote):
    conn = None
    returnValue = {"msg":"Err", "success":"error"}
    try:
        # sql_insert_query = "UPDATE {} SET delete_flag = True, modified_on={} WHERE quote_id = %s".format(config['msql_database']['table'], 'CURRENT_TIMESTAMP')
        sql_insert_query = "delete from {} where quote_id = %s".format(config['msql_database']['table'])
        conn = getDBConnection()
        cursor = conn.cursor()
        
        val = ( returnValidInput(objectQuote, "quote_id"),)
        cursor.execute(sql_insert_query, val)
        conn.commit()
        if cursor.rowcount > 0 :
            returnValue = {"msg":"Record Deleted", "success":True}
        else:
            returnValue = {"msg":"Nothing to Delete", "success":True}

    except Exception as e: 
        print(e)
        returnValue = False
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
    # print(returnValue)
    return returnValue


def pushDataToMongo(df):
    try:
        connection = getMongoDBConnection()
        my_database = connection.briqApp
        data = my_database.quote
        
        data.insert_many( df[df["rating"]>3].to_dict('records'))
        print("Mongo database Up & Running - Verified")
    except:
        print("Unable to connect to Mongo Database")


def getUnratedQuotes():
    conn = None
    records = None
    try:
        conn = mysql.connector.connect(user=config['msql_database']['username'], password=config['msql_database']['password'], host=config['msql_database']['host'], database=config['msql_database']['database'])
        cursor = conn.cursor()

        select_query = """SELECT quotes from {} where rating is null """.format(config['msql_database']['table'])
        cursor.execute(select_query)
        # columns = cursor.description 
        # records = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        records = cursor.fetchall()
        cursor.close()

    except Exception as err:
        print("Failed to read data from table", err)
    finally:
        if (conn):
            conn.close()
    return records
    # return dfObject

def recommendedQuotes():
    records = None
    try:
        connection = getMongoDBConnection()
        my_database = connection.briqApp
        data = my_database.quote
        cursor = data.find()
        records = pd.DataFrame(list(cursor))['quotes']
        # cursor = tweets.find(fields=['quotes'])
        # tweet_fields = ['id']

    except:
        print("Unable to connect to Mongo Database. ")
    return records

def getSimilarityQuotes():
    results = []

    unratedQuotes = getUnratedQuotes()
    ratedQuotes = pd.DataFrame(recommendedQuotes())
    
    for single in unratedQuotes:
        tempCopy = ratedQuotes.copy()
        try :
            tempCopy['Match'] = [cs.get_cosine(x, single[0]) for x in tempCopy["quotes"]]
            valueReturnSingle = (tempCopy.sort_values('Match', ascending=False).head(10)["Match"]).mean()*100
            if valueReturnSingle > 0:
                results.append({
                    "quote" : single[0],
                    "match_percentage": valueReturnSingle
                })
        except Exception as e:
            print(e)
    
    return results



