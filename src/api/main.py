
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from mongo_db import MongoDB

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION_NAME = 'walla_bikes'
MONGO_CLI = MongoDB(host='walla_mongo', port='27017', db_name='wallabot', user='admin', password='admin123')


@app.get('/bikes')
async def bikes():
    docs = MONGO_CLI.get(coll_name=COLLECTION_NAME, query={})

    bikes = []
    for i in docs:
        bikes.append(
            {
                'title': i['title'],
                'price': i['price'],
                'link': i['link'],
                'features': i['features']
            }
        )

    return bikes


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
