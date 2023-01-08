from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            links=[]
            for i in bigboxes[3:20]:
                link="https://www.flipkart.com"+i.div.div.div.a['href']
                links.append(link)

            reviews = []
            for link in links:
                prodRes = requests.get(link)
                prodRes.encoding='utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
                for commentbox in commentboxes[0:8]:
                    try:
                        name = commentbox.div.div.find('div', {'class':'row _3n8db9'}).div.p.text
                    except:
                        name = 'No Name'
                    try:        
                        rating = commentbox.div.div.find('div', {'class':'_3LWZlK _1BLPMq'}).text
                    except:
                        rating = 'No Rating'
                    try:            
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        custComment = commentbox.div.div.find_all('div', {'class': 't-ZTKy'})[0].text
                    except Exception as e:
                        print("Exception while creating dictionary: ",e)

                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                    reviews.append(mydict)

            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'Something is wrong. Please Contact the Developer'
    else:
        return render_template('index.html')

if __name__ == "__main__":
	app.run()
