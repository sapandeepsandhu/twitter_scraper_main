import glob
import pandas as pd

def merge_all_tweet_csvs():
    all_files = glob.glob("data/tweets_*.csv")
    df_list = [pd.read_csv(f) for f in all_files]
    combined = pd.concat(df_list, ignore_index=True)
    combined.to_csv("data/all_tweets_combined.csv", index=False)
    print(f"✅ Merged {len(df_list)} files into data/all_tweets_combined.csv")

if __name__ == "__main__":
    merge_all_tweet_csvs()
