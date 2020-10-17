# Assignment_Challenge

### Briq_Challenge

#### 1. Requirements

    1. Python 3.6
        > flask, pymongo, pandas, numpy, math, configparser, nltk
    2. MySQL
    3. Mongo
    
#### 2. Route
##### Required

    1. @app.route("/")
    2. @app.route("/GET_ALL_QUOTES", methods = ['POST', 'GET'])
    3. @app.route("/ADD_QUOTE", methods = ['POST'])
    4. @app.route("/RATE_QUOTE", methods = ['POST'])
    5. @app.route("/GET_RATED_QUOTES", methods = ['POST'])
    6. @app.route("/DELETE_QUOTES", methods = ['POST'])
    7. @app.route("/GET_RELATED_QUOTE")
    
#### 3. Run Flask Application
 0. Make sure the mongodb & mysql are connected to the application by the credentials
 1. python3 briqApp_2.py

#### 4. Code Walk through

1. The entire Application is controlled by the configuration file
  1. Intial run set `initial_run`. `no_of_run` to `0`
   > This would check for the inital database connection check.
   > It would import the excel data into MySQL Database. `Rating > 3` are sent to mongodb as recommendation quotes.
  2. NLTK libraries are downloaded for NLP task of similarity.
  
2. 4 files
 > `briqApp_Config.ini` - configuration file
 > `helper_briq_db.py`- db related functions
 > `cosine_similarity.py` - similarity algo
 > `briqApp_2.py` - main function
