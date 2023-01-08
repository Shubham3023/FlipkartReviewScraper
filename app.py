from logger import logging
from exception import CustomException
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd
from datetime import datetime
import os, sys

REVIEWS_DIR=os.path.join(os.getcwd(),"Reviews")

app = Flask(__name__)

logging.info("Creating route for HomePage")

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

logging.info("Creating route for Review Page")
@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            logging.info("Getting Search string from home page")
            searchString = request.form['content'].replace(" ","")
            logging.info("Adding search string to base url of flipkart")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            logging.info("Getting html data from flipkart using urlopen from urllib.request")
            uClient = uReq(flipkart_url)
            logging.info("Reading data from flipkart page")
            flipkartPage = uClient.read()
            logging.info("Parsing the data using html parser")
            flipkart_html = bs(flipkartPage, "html.parser")
            logging.info("Getting each product html code containing url of prodect page")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            logging.info("Creating a list to store product Links")
            links=[]
            for i in bigboxes[3:20]:
                logging.info("From each product block getting product url")
                link="https://www.flipkart.com"+i.div.div.div.a['href']
                logging.info("Appending link to links list")
                links.append(link)
            logging.info("Creating a list to store reviews data")
            reviews = []
            logging.info("Going through each link one by one and extracting data")
            for link in links:
                logging.info("Getting html code from each link")
                prodRes = requests.get(link)
                logging.info("Encoding the data with utf-8 format")
                prodRes.encoding='utf-8'
                logging.info("Parsing the text data")
                prod_html = bs(prodRes.text, "html.parser")
                logging.info("Finding all comment blocks from product page")
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
                logging.info("Going to each comment box to extract the review in that comment box")
                for commentbox in commentboxes[0:8]:
                    try:
                        logging.info("Getting name of Reviewer")
                        name = commentbox.div.div.find('div', {'class':'row _3n8db9'}).div.p.text
                    except:
                        name = 'No Name'
                    try:  
                        logging.info("Getting rating given by Reviewer")      
                        rating = commentbox.div.div.find('div', {'class':'_3LWZlK _1BLPMq'}).text
                    except:
                        rating = 'No Rating'
                    try:            
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        logging.info("Getting Review header")
                        commentHead = 'No Comment Heading'
                    try:
                        logging.info("Getting review")
                        custComment = commentbox.div.div.find_all('div', {'class': 't-ZTKy'})[0].text
                    except Exception as e:
                        raise CustomException(e,sys)
                    logging.info("Creating a dictionary to store all the data for each product")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                    logging.info("Appending the dictionary to a list")
                    reviews.append(mydict)
            logging.info("Making Review directory if it doesn't exists")
            os.makedirs(REVIEWS_DIR,exist_ok=True)
            logging.info("Preparing review file name")
            review_file_name = f"{searchString}_Reviews_{datetime.now().strftime('%m%d%Y__%H%M%S')}.csv"
            logging.info("Preparing Review file path")
            review_file_path = os.path.join(REVIEWS_DIR,review_file_name)
            logging.info("Creating Pandas dataframe containing reviews")
            df= pd.DataFrame(reviews[0:(len(reviews)-1)])
            logging.info("Saving dataframe to CSV")
            df.to_csv(review_file_path,index=False,header=True)

            logging.info("Returning the Reviews to results page")
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            raise CustomException(e, sys)
            
    else:
        return render_template('index.html')

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        raise CustomException(e,sys)
