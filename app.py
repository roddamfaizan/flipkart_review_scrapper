from flask import Flask, render_template, request
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

# Define the home page route
@app.route('/', methods=['GET'])
def homePage():
    """
    Render the home page.
    """
    return render_template("index.html")

# Define the review page route
@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    """
    Retrieve and display product reviews from Flipkart.
    """
    if request.method == 'POST':
        try:
            # Get the search query from the form
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            # Open the Flipkart URL and scrape the page
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")

            # Extract product information
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")

            # Extract and parse product reviews
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            reviews = []

            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}

                reviews.append(mydict)

            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'Something went wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
