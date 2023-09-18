import os

from time import time

import pandas as pd
from sqlalchemy import create_engine


def ingest_callable(user, password, host, port, db, table_name, parquet_file, execution_date):
    print(table_name, parquet_file, execution_date)

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()

    print('connection established successfully, inserting data...')

    t_start = time()
    df = pd.read_parquet(parquet_file)

    print(df.head())

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    #df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.head(1000).to_sql(name=table_name, con=engine, if_exists='replace')

    t_end = time()
    print('inserted the data, took %.3f second' % (t_end - t_start))

    # df.to_sql(name=table_name, con=engine, if_exists='append')
    #
    # while True:
    #     t_start = time()
    #
    #     try:
    #         df = next(df_iter)
    #     except StopIteration:
    #         print("completed")
    #         break
    #
    #     df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    #     df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    #
    #     df.to_sql(name=table_name, con=engine, if_exists='append')
    #
    #     t_end = time()
    #
    #     print('inserted another chunk, took %.3f second' % (t_end - t_start))
