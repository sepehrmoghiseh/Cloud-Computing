from flask import Flask
from flask_restful import Api
import mysql.connector
import pika
import mysql.connector
import requests
import boto3
import logging
from botocore.exceptions import ClientError

s3_client = None
logging.basicConfig(level=logging.INFO)


def imageTag(body):
    api_key = 'acc_c4543bae6c8a0cb'
    api_secret = 'cc8f4b915742a900d20cb7b1aeb2d7ef'
    image_path = downloadPath(body)
    response = requests.post(
        'https://api.imagga.com/v2/tags',
        auth=(api_key, api_secret),
        files={'image': open(image_path, 'rb')})
    for i in range(len(response.json()['result']['tags'])):
        if 'vehicle' == response.json()['result']['tags'][i]['tag']['en']:
            if response.json()['result']['tags'][i]['confidence'] >= 50:
                id = int(body[:body.index('.')])
                return updateState(id, response.json()['result']['tags'][0]['tag']['en'], 1)
            else:
                break
    else:
        id = int(body[:body.index('.')])
        return updateState(id, response.json()['result']['tags'][0]['tag']['en'], 0)


def downloadPath(name):
    logging.basicConfig(level=logging.INFO)

    try:
        s3_resource = boto3.resource(
            's3',
            endpoint_url='https://s3.ir-thr-at1.arvanstorage.com',
            aws_access_key_id='65a0c54d-5ad8-429b-989d-ea431d6c92aa',
            aws_secret_access_key='b0733d9e84cd241c1dced64bb8ebda629146eaa14af94751618879e7eeb2c32a'
        )
    except Exception as exc:
        logging.error(exc)
    else:
        try:
            # bucket
            bucket = s3_resource.Bucket('adproj')

            object_name = name
            download_path = r"D:\\downloadpic\\" +name

            bucket.download_file(
                object_name,
                download_path
            )
        except ClientError as e:
            logging.error(e)

    return download_path


def emailSend(id):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM advertisement where id=%d" % id)
    myresult = mycursor.fetchall()
    email = myresult[0][1]
    if myresult[0][3] == "approved":
        return requests.post(
            f"https://api.mailgun.net/v3/sandbox4599c15e91b84741934ddfbb06294706.mailgun.org/messages",
            auth=("api", "da931677552175c26b61b555c8268001-48c092ba-d854d79b"),
            data={"from": "<mailgun@sandbox4599c15e91b84741934ddfbb06294706.mailgun.org>",
                  "to": [email],
                  "subject": "your ad status has been updated",
                  "text": "hello! your ad with id " + str(id) + " has been approved!"})
    else:
        return requests.post(
            f"https://api.mailgun.net/v3/sandbox4599c15e91b84741934ddfbb06294706.mailgun.org/messages",
            auth=("api", "da931677552175c26b61b555c8268001-48c092ba-d854d79b"),
            data={"from": "<mailgun@sandbox4599c15e91b84741934ddfbb06294706.mailgun.org>",
                  "to": [email],
                  "subject": "your ad status has been updated",
                  "text": "hello! your ad with id " + str(id) + " has been rejected!"})


def receive():
    connection = pika.BlockingConnection(
        pika.URLParameters("amqps://vohuihdu:CfIzR9UiAxbKoCVOWSKZAYPkLJ9LZlu-@codfish.rmq.cloudamqp.com/vohuihdu"))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        id = imageTag(str(body)[2:-1])
        emailSend(id)

    channel.basic_consume(queue='ads', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


def updateState(id, tag, flag):
    global mydb
    mydb = mysql.connector.connect(
        host="mysql-2018f905-sepehrmoghiseh-faac.aivencloud.com",
        port=23657,
        user="avnadmin",
        password="AVNS_V0YBXVcFNWlqINBgyHF",
        database="defaultdb"
    )

    mycursor = mydb.cursor()
    query = """update advertisement set category=%s, state=%s where id=%s"""
    if flag == 1:
        value = (tag, "approved", id)
    else:
        value = (tag, "rejected", id)

    mycursor.execute(query, value)
    mydb.commit()
    return id


app = Flask(__name__)
api = Api(app)
if __name__ == "__main__":
    receive()
    app.run(debug=True)
