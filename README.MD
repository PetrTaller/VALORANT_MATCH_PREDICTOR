### VALORANT Match Winner Predictor ###

## Overview ##

The VALORANT Match Winner Predictor is a web-based application built using Streamlit that predicts the winner of a VALORANT match based on selected team and match parameters. Users can choose from multiple machine learning models to generate predictions.

## Features ##

Model Selection: Choose from Logistic Regression, Random Forest, XGBoost, and a Sequential Neural Network.

Historical Data Analysis: Uses past match statistics to make predictions.

Custom Input Selection: Select teams, maps, patch version, and league details.

Graphical Insights: View model accuracy based on the number of records.

## Tech Stack ##

Frontend: Streamlit (Python-based web UI)

Backend: Pandas for data handling, Joblib/TensorFlow for model loading

Models: Logistic Regression, Random Forest, XGBoost, Sequential (Keras-based)

## Setup Instructions ##

1. Clone the Repository

git clone https://github.com/PetrTaller/VALORANT_MATCH_PREDICTOR
cd VALORANT_MATCH_PREDICTOR

2. Install Dependencies

pip install -r requirements.txt

3. Run the Application

python -m streamlit run app.py

## File Structure ##

VALORANT_MATCH_PREDICTOR/
│-- app.py                          # Main entry point for the Streamlit app
│-- requirements.txt                # Python dependencies
│-- README.MD                       # Documentation for the project
│-- data/                            
│   ├── teams.csv                   # Team information
│   ├── maps.csv                    # Map details
│   ├── leagues.csv                 # League information
│   ├── patches.csv                 # Patch version details
│   ├── matches300.csv              # Past match statistics
│   ├── matches10353.csv            # Past match statistics
│   ├── model_accuracy.csv          # model accuracy statistics
│   ├── crawler/                    # crawlers and other data
│   │   ├──matchdatascraper.py      # crawler for scraping data from matches
│   │   ├── ....          
│-- src/
│   ├── models/                     # Machine learning models
│   │   ├── logistic_regression.pkl
│   │   ├── random_forest_classifier.pkl
│   │   ├── xgboost_classifier.pkl
│   │   ├── sequential_model.h5
│-- doc/
│   ├── colab/                      # Team notebook used for model learning
│   ├── test/                       # Test cases and reports

## Usage ##

Select Team 1 and Team 2 from the dropdown menus.

Choose from one to three maps for the match (bigger accuracy with all three maps selected).

Select the patch version and league (the latest patch is recommended).

Pick a machine learning model for prediction (use the model).

Pick the number of data (300 is better but doesnt have all of the teams).

Click Predict Winner to see the result.

## Known Issues & Future Enhancements ##

Add support for real-time match updates
Add an option to select an upcoming match to predict
Fix Sequential and Xgboost model
Enhance UI
Create a better model for more accurate predictions. Maybe change the input data if it improves the accuracy, 
    and also the crawler to scrape said data
Go online (Put the web online for users to predict)

## Contributors ##

[Petr Taller] - Developer

## License ##

This project is licensed under the MIT License.

## Sources ##

Data - https://www.vlr.gg/matches/results (data extracted using two crawlers in the "/data/crawler" folder)

Machine learning models - Courses from SPSEJECNA Moodle (Courses made by [Ing. Ondřej Mandík], and [Mgr. Alena Reichlová]).

Streamlit.io documentation - https://docs.streamlit.io/
 --- https://docs.streamlit.io/get-started/installation/command-line
 --- https://docs.streamlit.io/get-started/fundamentals

Matplotlib's Pyplot tutorial - https://matplotlib.org/stable/tutorials/pyplot.html

Pandas cheat sheet - https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf

Youtube - https://www.youtube.com
 --- https://www.youtube.com/watch?v=3Xc3CA655Y4

ChatGPT - https://chatgpt.com
 --- https://chatgpt.com/share/67f2f49b-e3b0-800e-a2fd-8e441df6c764
 --- https://chatgpt.com/share/67f2f58e-218c-800e-9772-d6c07d6e9171

## comments for my personal use (not important) ##
(python -m venv "C:\Users\talle\OneDrive\PV\ML_VALORANT_MATCHES\.venv")
python -m pip install streamlit scikit-learn pandas numpy matplotlib joblib xgboost
C:\Users\talle\OneDrive\PV\ML_VALORANT_MATCHES\.venv\Scripts\activate
cd "C:\Users\talle\OneDrive\PV\ML_VALORANT_MATCHES"
python -m streamlit run c:/Users/talle/OneDrive/PV/ML_VALORANT_MATCHES/src/app.py
