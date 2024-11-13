
## DSS5105 Pioneer Group Project


# Automated ESG Data Extraction and Performance Analysis


```
pip freeze > requirements.txt
```

#### Create your venv for this project

```
python -m venv venv

# for macos
source venv/bin/activate

# for windows
.\venv\Scripts\Activate

pip install -r requirements.txt
```

#### Quit the venv
```
deactivate
```

## To run the dashboard web app

```
cd groupB/dashboard/client
npm install
npm start

cd groupB/dashboard/server
npm install
npm start
```

## Run the dashboard web app Frontend and Backend simultaneously

```
cd groupB/dashboard
npm install
npm start
```


## Dockerize Node.js Backend Server
```
cd groupB/dashboard/server

docker build -t pioneer-server-1 .

docker run -d \
--name pioneer-server-1 \
-p 5105:5105 \
-v "$(pwd)/pioneer_key.json:/usr/src/app/pioneer_key.json" \
--env-file .env \
--log-driver json-file \
--log-opt max-size=10m \
pioneer-server-1
```

## Dockerize Python API
```
docker build -t pioneer-server-2 .

docker run -d \
  --name pioneer-server-2 \
  --gpus all \
  -p 5106:5106 \
  pioneer-server-2
```

## Dockerize Frontend
```
cd groupB/dashboard/client

docker build -t pioneer-frontend .

docker run -d \
  --name pioneer-client \
  -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:5106 \
  pioneer-client
```