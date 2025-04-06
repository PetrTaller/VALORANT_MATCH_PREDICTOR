import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import joblib
import time
import xgboost
#from tensorflow.keras.models import load_model #Uncomment for Sequential model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/models')))

class Site:

    def load_datasets():
        # Load datasets
        try:
            teams = pd.read_csv("data/teams.csv")
            maps = pd.read_csv("data/maps.csv")
            leagues = pd.read_csv("data/leagues.csv")
            model_accuracy = pd.read_csv("data/model_accuracy.csv")
            patches = pd.read_csv("data/patches.csv")
            return teams,maps,leagues,model_accuracy,patches
        except Exception as e:
            return f"Error during extraction of datasets: {str(e)}"
    
    # Load datasets
    teams,maps,leagues,model_accuracy,patches = load_datasets()

    # Sort maps and leagues for selection, and create map-to-id and league-to-id dictionaries
    def dict_create(maps,teams,leagues):
        try:
            map_dict = dict(zip(maps["map"], maps["id"]))
            team_dict = dict(zip(teams["team"], teams["id"]))
            league_dict = dict(zip(leagues["league"], leagues["id"]))
            sorted_maps = sorted(maps["map"].tolist())
            sorted_leagues = sorted(leagues["league"].tolist())
            return map_dict,team_dict,league_dict,sorted_maps,sorted_leagues
        except Exception as e:
            return f"Error during extraction of datasets: {str(e)}"

    map_dict,team_dict,league_dict,sorted_maps,sorted_leagues = dict_create(maps,teams,leagues)

    # Define models
    models = {
        "Logistic Regression": "src/models/logistic_regression_model.pkl",
        "Random Forest": "src/models/random_forest_classifier.pkl",
        "XGBoost": "src/models/xgboost_model.pkl",
        "Sequential": "src/models/sequential_model.h5"
    }

    def load_matches(file):
        try:
            matches_data = pd.read_csv(file)
            matches_data.fillna(0, inplace=True)
            matches_data = matches_data[matches_data['winner'] != 0.5]
            matches_data.drop(columns=["match_url"], inplace=True)

            # Calculate team stats using past matches
            team1_stats = matches_data[['team1', 'AVG_KD1', 'AVG_ACS1']].rename(columns={'team1': 'team', 'AVG_KD1': 'KD', 'AVG_ACS1': 'ACS'})
            team2_stats = matches_data[['team2', 'AVG_KD2', 'AVG_ACS2']].rename(columns={'team2': 'team', 'AVG_KD2': 'KD', 'AVG_ACS2': 'ACS'})

            # Combine both team1 and team2 stats into a single dataset
            team_stats = pd.concat([team1_stats, team2_stats])

            # Group by team ID and calculate mean KD & ACS
            team_stats = team_stats.groupby('team').mean().reset_index()
            
            # Merge team statistics into the dataset for team1
            matches_data = matches_data.merge(team_stats, left_on='team1', right_on='team', how='left').rename(columns={'KD': 'team1_KD', 'ACS': 'team1_ACS'}).drop(columns=['team'])
            
            # Merge team statistics into the dataset for team2
            matches_data = matches_data.merge(team_stats, left_on='team2', right_on='team', how='left').rename(columns={'KD': 'team2_KD', 'ACS': 'team2_ACS'}).drop(columns=['team'])
            
            return matches_data,team_stats
        except Exception as e:
            return f"Error during extraction of data: {str(e)}"


    def load_ml_model(model_name,models=models):
        model_path = models[model_name]

        if model_name == "Sequential":
            #return load_model(model_path)  # Load .h5 model properly # Uncomment when for use of the Sequential model
            return None # Comment for use of Sequential model
        else:
            return joblib.load(model_path)

    def predict_winner(team1, team2, map1, map2, map3, patch, league, model,data_num,team1_name,team2_name,load_matches=load_matches):

        # Retrieve team stats from past matches
        matches,team_stats = load_matches(f"data/matches"+data_num+".csv")
        team1_data = team_stats[team_stats['team'] == team1]
        team2_data = team_stats[team_stats['team'] == team2]

        if team1_data.empty or team2_data.empty:
            return "Can't be determined. One or both teams have no historical data. Change the number of records to highest or contact the owner if issue remains."

        team1_KD, team1_ACS = team1_data[['KD', 'ACS']].values[0]
        team2_KD, team2_ACS = team2_data[['KD', 'ACS']].values[0]

        # Create input DataFrame
        input_data = pd.DataFrame([[team1_KD, team2_KD, team1_ACS, team2_ACS, map1, map2, map3, patch, league]],
                                  columns=['team1_KD', 'team2_KD', 'team1_ACS', 'team2_ACS', 'map1', 'map2', 'map3', 'patch', 'league'])

        # Convert the DataFrame to a NumPy array (without column names)
        input_data_array = input_data.to_numpy()

        # Ensure the model accepts the correct input format
        if team1_name == None or team2_name == None:
            return f"Two teams have to be predicted for prediction."
        else:
            try:
                winner = model.predict(input_data_array)[0]
                return team1_name if winner == 1 else team2_name
            except Exception as e:
                return f"Error during prediction: {str(e)}"

    def site(time_to_predict,teams=teams,sorted_maps=sorted_maps,map_dict=map_dict,patches=patches,sorted_leagues=sorted_leagues,models=models,team_dict=team_dict,league_dict=league_dict,model_accuracy=model_accuracy,predict_winner=predict_winner):

        # Streamlit UI
        st.title("VALORANT Match Winner Predictor")

        # User input with validation for different teams, maps, and leagues

        col1, col2= st.columns([1, 1])
        with col1:
            team1_name = st.selectbox("Select First Team", teams["team"].tolist())
        with col2:
            team2_name = st.selectbox("Select Second Team", [team for team in teams["team"].tolist() if team != team1_name])

        #################### MAP LOGIC

        # Allow users to select 0 to 3 maps
        selected_maps = st.multiselect("Select Up to 3 Maps in correct order", sorted_maps)
        if len(selected_maps) > 3:
                st.warning("You selected more than 3 maps. Only the first 3 maps will be used.")
        # Limit selection to 3 maps
        selected_maps = selected_maps[:3]  # Ensure max 3 selections

        # Convert selected names to IDs
        selected_map_ids = [map_dict[m] for m in selected_maps]

        # Ensure exactly 3 values by filling missing ones with 0
        while len(selected_map_ids) < 3:
            selected_map_ids.append(0)

        # Unpack into variables safely
        map1, map2, map3 = selected_map_ids[0], selected_map_ids[1], selected_map_ids[2]

        ######################### MAP LOGIC

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            patch = st.selectbox("Enter Patch Version", patches["patch"].tolist())
        with col2:
            league_name = st.selectbox("Select League", sorted_leagues)
        with col3:
            model_choice = st.selectbox("Choose a Model", list(models.keys()))
            data_choice = st.selectbox("Choose the number of records for the model", {"300","10353"})

        if patch < 10.05:
                st.warning("The newest patch is recommended for predicting upcoming matches.")

        if model_choice == "Sequential":
                st.error("This model isn't available for the current version of the site")

        # Convert league name and team names to its corresponding ID
        team1 = team_dict[team1_name]
        team2 = team_dict[team2_name]
        league = league_dict[league_name]

        if st.button("Predict Winner"):
            with st.spinner("Predicting..."):
                time.sleep(int(time_to_predict))
            st.empty()
            selected_map_ids = selected_map_ids[:3]
            map1, map2, map3 = selected_map_ids
            try:
                model = joblib.load(models[model_choice])
                if model is not None:
                    prediction_result = predict_winner(team1, team2, map1, map2, map3, patch, league, model,data_choice,team1_name,team2_name)
                    st.balloons()
                    st.markdown(f"""
                        <div style="padding:20px; border-radius:10px; text-align:center; border-color:red; border-style: solid;">
                            <h2 style="color:white;">🎉 Prediction Complete 🎉</h2>
                            <h1 style="color:white;">🏆 {prediction_result} 🏆</h1>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Model is not available for prediction. ❌")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)} , try to use a different model and contact the owner about this error if it remanis❌")


        model_accuracy_pivot = model_accuracy.pivot(index='records', columns='model', values='accuracy')

        # Plotting the graph
        st.title("Model Accuracy Chart")

        # Create the plot for each model
        plt.figure(figsize=(10,6))
        for model in model_accuracy_pivot.columns:
            plt.plot(model_accuracy_pivot.index, model_accuracy_pivot[model], label=model)

        # Add labels and a title
        plt.xlabel('Number of Records')
        plt.ylabel('Accuracy')
        plt.title('Accuracy vs. Number of Records for Each Model')

        # Add a legend
        plt.legend()

        # Display the plot in Streamlit
        st.pyplot(plt)

if __name__ == "__main__":
    Site.site(2)