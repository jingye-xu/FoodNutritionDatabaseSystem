# FoodNutritionDatabaseSystem
This is a project for the database class. 
Motivaiton: for a healthy life, we want to monitor and control what main nutrients we take in every day. Therefore, we want to design this food nutrition database, which contains basic food nutrition information, such as how much protein or calories are in 100g of boiled eggs.

## Usage
### 1. Generate self-signed certificates
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### 2. Run local database with docker
```bash
sudo docker run -d -p 27018:27017 --name mongo mongo:latest
```
### 3. Modify local_config.py file


### 4. Build docker image
```bash
sudo docker build --tag foodinfo .
```

### 5. Run foodinfo web server
```bash
sudo docker run -d -p 8000:5000 foodinfo
```
