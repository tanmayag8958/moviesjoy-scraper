from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import datetime
import boto3
import json
import uuid
from boto3.dynamodb.conditions import Key, Attr

def gettingLink(completeContent):

    downContent = []
    
    for i in completeContent:
        page = requests.get(i["link"])
        content = BeautifulSoup(page.content, 'html.parser')
        downPage = content.select('.fasc-button')

        oneDownContent = ""
        for j in downPage:
            oneDownContent += "<a href='" + str(j["href"]) + "'><button class='btn btn-primary'>" + str(j.get_text().strip()) + "</button>"
            # oneDownContent["downLink"].append(j["href"])

        downContent.append(oneDownContent)

    return downContent


def deal_scrape():
    page = requests.get("https://moviesjoy.in/category/amazon-prime/")
    content = BeautifulSoup(page.content, 'html.parser')
    completeContent = []

    homeContent = content.select('.bw_thumb_title')

    for i in range(len(homeContent)):
        homeContent[i].select('.bw_thumb')[0].find('a', href=True)
        oneThumb = {
            "contentName" : homeContent[i].select('.bw_thumb')[0].find('a', href=True)["title"],
            "image" : homeContent[i].select('.tm_hide')[0]["src"],
            "link" : homeContent[i].select('.bw_thumb')[0].find('a', href=True)["href"],
        }

        completeContent.append(oneThumb)

    downloadLink = gettingLink(completeContent)

    return completeContent, downloadLink












def scrape(event, context):
    completeContent, downloadLink = deal_scrape()
    print(completeContent)
    table = boto3.resource('dynamodb').Table('moviesjoy')
    newMovies = []
    newMoviesMail = """
 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="https://www.w3.org/1999/xhtml">
<head>
<title>YTS Scraper</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="viewport" content="width=device-width, initial-scale=1.0 " />
<style>
body {
	margin: 0 !important;
	padding: 0 !important;
	-webkit-text-size-adjust: 100% !important;
	-ms-text-size-adjust: 100% !important;
	-webkit-font-smoothing: antialiased !important;
    text-decoration: none;
}
img {
	border: 0 !important;
	outline: none !important;
}
.bgclr{
    background-color: #171717;
}
                    .btn {
                        border-radius: 10px;
                        padding: 10px 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        margin: 4px 4px;
                        cursor: pointer;
                        color: white;
                        font-weight: bold;
                        text-decoration: none;
                    }
                    .btn-primary {
                        font-size: 13px;
                        background-color: #008CBA;
                    }
                    .btn-success {
                        text-decoration: none;
                        font-size: 20px;
                        color: #0c9100;
                        
                    }
                    a{
                        text-decoration: none;
                    }
                    
                </style>
</head>
            <body style="margin:0px; padding:0px;" bgcolor="#171717"> 
            <center>
            <div class='bgclr'>
    """
    for i, movie in enumerate(completeContent, 0):
        responseGet = table.get_item(
        Key={
                'contentName': movie["contentName"],
            }
        )
        if responseGet['ResponseMetadata']['HTTPHeaders']['content-length'] != '2':
            print("------GetItem------------")
            print(responseGet['Item'])
            print("-------GetItem--------------")
        else:
            # print (movie)
            newMovies.append(movie)
            newMoviesMail +=  "<div class='bgclr'><br/><a href='" + movie['link'] + "'> <img src='" + movie['image'] + "'height='200'/><br/><br/><span class='btn-success'>" + movie['contentName'] + " </span></a><br/><br/>" + downloadLink[i] + "<br/><br/></div><br/><br/> "
            print("---------New Movie---------")
            print(movie)
            print("---------New Movie---------")
        responsePut = table.put_item(
        Item=movie
        )

#   file_name = f"deals-{data['date']}"
#   save_file_to_s3('ebay_daily_deals', file_name, data)
    print(f"Newmovies :  {newMovies}")

    # for i in data:
    #     print(i["magnetLink"])
    newMoviesMail += """
            </div>
            </br>
            </br>
            <small color='white'>
                - from your humble scraper bot
            </small>
            </center>
            </body>
        </html>
    """

    if newMovies:
        client = boto3.client('ses')
        name = 'moviesjoy-Scaper'
        source = 'rocktanmay800@gmail.com'
        subject = 'New Contant : moviesjoy-scraper'
        destination = 'rocktanmay800@gmail.com'
        message = newMoviesMail
            
        response = client.send_email(
            Destination={
                'ToAddresses': [destination,'sneheelshivam@gmail.com', "shaurya96gairola@gmail.com","rambospartan72@gmail.com"],
                },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': message,
                        },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=source,
        )
    
    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps('Updated')
    }































# completeContent, downloadLink = deal_scrape()

# print(completeContent, end = "\n\n")
# print(downloadLink, end = "\n\n")