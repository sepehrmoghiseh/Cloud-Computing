from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS

spark = SparkSession \
    .builder \
    .appName("game Suggest") \
    .getOrCreate()

game_df = spark.read.csv('games.csv', header=True).cache()
rating_df = spark.read.csv('ratings.csv', header=True).cache()
rating_df = rating_df.withColumn("user_id", rating_df["user_id"].cast('int'))
rating_df = rating_df.withColumn("game_id", rating_df["game_id"].cast('int'))
game_df = game_df.withColumn("game_id", game_df["game_id"].cast('int'))
rating_df = rating_df.withColumn("rating", rating_df["rating"].cast('int'))

(training, test) = rating_df.randomSplit([0.8, 0.2])
rating_df.registerTempTable("ratings")
game_df.registerTempTable("games")
jdf = spark.sql("select * from games inner join ratings using (game_id)")
jdf.registerTempTable('join')

als = ALS()
als.setMaxIter(2)
als.setRegParam(0.01)
als.setUserCol("user_id")
als.setItemCol('game_id')
als.setRatingCol("rating")
alsModel = als.fit(training)
alsModel.setColdStartStrategy("drop")
predictions = alsModel.transform(test)

userid = input('enter> ')
userRecs = alsModel.recommendForUserSubset(jdf.where(jdf.user_id == int(userid)), 5)
search = userRecs.collect()

for i in range(5):
    print(game_df.select('name').where(game_df.game_id == search[0][1][i][0]).collect())
