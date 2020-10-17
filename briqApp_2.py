

from flask import Flask, request, jsonify

import helper_briq_db as db_helper

import configparser
config = configparser.ConfigParser()
config.read('briqApp_Config.ini')

if not db_helper.checkForConnectionToMySQL():
    print("Unable to connect to MySQL Database")
    exit()

if config['initial_run']['no_of_run'] == "0":
    if not db_helper.checkForTable():
        print("Unable to Find MySQL Table ")
        exit()
    try:
        db_helper.ImportAllDataFromExcelToMySQL()
        print("MySQL Data Import - Complete ")
    except Exception as e:
        print(e)
        exit()


app = Flask(__name__)

@app.route("/")
def hello():
    return db_helper.helloWorld()


@app.route("/GET_ALL_QUOTES", methods = ['POST', 'GET'])
def fetchCommand():
    return jsonify( {"data": db_helper.getAllQuote({}), "msg" : "OK" })


@app.route("/ADD_QUOTE", methods = ['POST'])
def insertCommand():
    quoteObject = request.get_json()
    if ('quotes' not in quoteObject) or ('addedBy' not in quoteObject ):
        return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Insufficient Details" })    

    if db_helper.insertQuote(quoteObject):
        return jsonify( {"data": request.get_json(), "msg": "OK" })
    
    return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Could not insert record" })


# RATE QUOTE
@app.route("/RATE_QUOTE", methods = ['POST'])
def updateRatingCommand():
    quoteObject = request.get_json()
    if ('rating' not in quoteObject) or ('quote_id' not in quoteObject ):
        return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Insufficient Details" })    

    if quoteObject['rating'] not in range(1,6):
        return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Kindly rate appropriately" })    

    if db_helper.updateQuote(quoteObject):
        return jsonify( {"data": request.get_json(), "msg": "OK" })
    
    return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Could not update record" })


# Fetch RATED QUOTES BY USERS
@app.route("/GET_RATED_QUOTES", methods = ['POST'])
def fetchRatedQuotesByUserCommand():
    quoteObject = request.get_json()
    if 'addedBy' not in quoteObject :
        return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Insufficient Details" })    

    return jsonify( {"data": db_helper.getRatedQuotesByUser(quoteObject), "msg" : "OK" })


@app.route("/DELETE_QUOTES", methods = ['POST'])
def deleteCommand():
    quoteObject = request.get_json()
    if 'quote_id' not in quoteObject :
        return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Insufficient Details" }) 

    responseObject = db_helper.removeQuotes(quoteObject)
    if responseObject["success"]:
        return jsonify( {"data": responseObject, "msg": "OK" })
    
    return jsonify( {"data": request.get_json(), "msg": "Err", "ErrorMessage": "Could not Delete record" })

@app.route("/GET_RELATED_QUOTE")
def similarCommand():
    
    return jsonify( {"data": db_helper.getSimilarityQuotes(), "msg": "OK" })

if __name__ == '__main__':
    app.run(port= config['serve_run']['port'])