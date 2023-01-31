from botocore.exceptions import ClientError
from flask import Flask, request
from flask_restful import Api
import boto3
import logging
import pika
import imghdr
import mysql.connector

s3_client = None
logging.basicConfig(level=logging.INFO)


def necessaryConnection():
    global mydb
    mydb = mysql.connector.connect(
        host="mysql-2018f905-sepehrmoghiseh-faac.aivencloud.com",
        port=23657,
        user="avnadmin",
        password="AVNS_V0YBXVcFNWlqINBgyHF",
        database="defaultdb"
    )
    global connection
    connection = pika.BlockingConnection(
        pika.URLParameters("amqps://vohuihdu:CfIzR9UiAxbKoCVOWSKZAYPkLJ9LZlu-@codfish.rmq.cloudamqp.com/vohuihdu"))
    global channel
    channel = connection.channel()
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    try:
        global s3_client
        s3_client = boto3.client(
            's3',
            endpoint_url='https://s3.ir-thr-at1.arvanstorage.com',
            aws_access_key_id='65a0c54d-5ad8-429b-989d-ea431d6c92aa',
            aws_secret_access_key='b0733d9e84cd241c1dced64bb8ebda629146eaa14af94751618879e7eeb2c32a'
        )

    except Exception as exc:
        logging.error(exc)
    global s3_resource
    s3_resource = boto3.resource(
        's3',
        endpoint_url='https://s3.ir-thr-at1.arvanstorage.com',
        aws_access_key_id='65a0c54d-5ad8-429b-989d-ea431d6c92aa',
        aws_secret_access_key='b0733d9e84cd241c1dced64bb8ebda629146eaa14af94751618879e7eeb2c32a'
    )


def dbManagement(select, email=None, des=None, image=None, what=None, id=None):
    if select == 1:

        mycursor = mydb.cursor()

        sql = "INSERT INTO advertisement (email, description,state,adPic) VALUES (%s, %s,%s,%s)"
        val = (email, des, "not approved", "." + str(what))
        mycursor.execute(sql, val)
        sql = "SELECT MAX(Id) FROM advertisement"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        res = myresult[0]
        res = str(res)
        saveName = res[1:-2] + "." + what
        uploadImg(image, saveName)
        mydb.commit()
        rabbitqueue(saveName)
        return "your ad has been registered with id " + res[1:-2]

    else:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM advertisement where id=%d" % id)
        myresult = mycursor.fetchall()
        if myresult[0][3] == 'not approved':
            return "your ad is not approved yet!"
        elif myresult[0][3] == "rejected":
            return "your ad is rejected!"
        else:
            url = preSign(str(id) + myresult[0][5])
            return "here is your ad info \n" \
                   "description: " + myresult[0][2] + "\n" \
                                                      "category: " + str(myresult[0][4]) + "\n" \
                                                                                           "image: " + url + "\n" \
                                                                                                             "state: approved"


def rabbitqueue(id):
    channel.basic_publish(exchange='', routing_key='ads', body=id)


def preSign(name):
    try:
        bucket = 'adproj'
        object_name = name

        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': object_name
            },
            ExpiresIn=604800
        )
    except ClientError as e:
        logging.error(e)
    return response


def uploadImg(file, name):
    bucket = s3_resource.Bucket('adproj')
    object_name = str(name)

    bucket.put_object(
        ACL='private',
        Body=file,
        Key=object_name
    )


app = Flask(__name__)
api = Api(app)


@app.route('/adpost', methods=['POST'])
def postAd():
    email = request.form.get('email')
    des = request.form.get('description')
    image = request.files.get('image')
    what = str(imghdr.what(image))
    return dbManagement(1, email, des, image, what)


@app.route('/adget', methods=['get'])
def getAd():
    id = request.form.get('id')
    return dbManagement(2, id=int(id))


if __name__ == "__main__":
    necessaryConnection()
    app.run(debug=True)
