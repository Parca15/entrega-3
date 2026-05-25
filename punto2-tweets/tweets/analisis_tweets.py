from tweet_pipeline import TweetPipeline


if __name__ == '__main__':
    pipeline = TweetPipeline(csv_path='data/tweets_raw.csv', output_dir='resultados')
    pipeline.run()
