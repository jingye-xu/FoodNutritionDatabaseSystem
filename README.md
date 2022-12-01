# FoodNutritionDatabaseSystem
This is a project for the database class. 

## Motivaiton: 
For a healthy life, we want to monitor and control what we take in every day, especially those who are dieting or have special health conditions. Therefore, we design this food nutrition database, which contains basic food nutrition information, such as how much protein or calories are in 100g of boiled egg, and some advanced features:

1)	Users can register, log in, and log out the system.
2)	User can search for a food/dish and get the basic nutrition information about it. To search for a dish, please search for the main ingredients of the dish. Note that the dish search function is only available after user login.
3)	User can add/delete a food. For example, if Cheeto is not in the system, user can create a food with name Cheeto and its nutrition information. Note that the food adding/removing function is only available after user login.
4)	User can change the number of servings of a food and get the nutrition information for different number of servings. For example, how much protein 100g milk contains and how much protein 200g milk contains. Note that the changing serving size function is only available after user login.


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
