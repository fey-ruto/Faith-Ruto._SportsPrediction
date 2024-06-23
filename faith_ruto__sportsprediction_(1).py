# -*- coding: utf-8 -*-
"""Faith Ruto._SportsPrediction (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IrMoHC65Ee_KVIcfrkfxXCF-fyMOhiSN
"""

import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score,GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score ,mean_absolute_error
from flask import Flask, request, jsonify
import joblib
import warnings
import matplotlib.pyplot as plt

"""# Step 1:Loading Datasets"""

from sklearn.model_selection import train_test_split
from google.colab import drive
drive.mount('/content/drive')

!ls

players = pd.read_csv("/content/drive/My Drive/players_22.csv") #player_22
legacy = pd.read_csv("/content/drive/My Drive/male_players.csv") #male_legacy

players.shape

legacy.shape

"""# Describe the datasets"""

players.describe()

legacy.describe()

"""# Display Information about the Dataframes"""

players.info()

legacy.info()

players =pd.DataFrame(players)

players

legacy =pd.DataFrame(legacy)

legacy

players.dtypes

legacy.dtypes

"""# Step 2: Cleaning the Data

# Dropping Unneccessary Columns in Legacy Dataset
"""

legacy.columns

legacy.drop(columns = ['player_id', 'player_url', 'fifa_version', 'fifa_update', 'fifa_update_date', 'player_face_url', 'short_name', 'long_name'], inplace = True)

legacy.info()

"""# Fill missing values for numerical columns with median and for categorical columns with mode in both Datasets"""

legacy.fillna(legacy.median(numeric_only=True), inplace=True)
legacy.fillna(legacy.mode().iloc[0], inplace=True)
players.fillna(players.median(numeric_only=True), inplace=True)
players.fillna(players.mode().iloc[0], inplace=True)

"""# Convert relevant Columns to Categorical"""

position_columns = ['ls', 'st', 'rs', 'lw', 'lf', 'cf', 'rf', 'rw', 'lam', 'cam', 'ram',
                    'lm', 'lcm', 'cm', 'rcm', 'rm', 'lwb', 'ldm', 'cdm', 'rdm', 'rwb',
                    'lb', 'lcb', 'cb', 'rcb', 'rb', 'gk']

for col in position_columns:
    legacy[col] = legacy[col].astype('category')
    players[col] = players[col].astype('category')

"""# Step 3: Feature Extraction"""

y = legacy['overall'] #our target variable

"""# Get and Process all Quantitative Data"""

quant = legacy.select_dtypes(include = [np.number])

"""# Perform Correlation Analysis"""

corr_matrix = quant.corr()

corr_matrix['overall'].sort_values(ascending = False)

"""# Dropping columns that have a correlation less than 0.4 and greater than -0.4"""

for column in quant.columns:
  if corr_matrix['overall'][column] < 0.4 and corr_matrix['overall'][column] > -0.4:
    quant.drop(column, axis = 1, inplace = True)

quant.info()

corr_matrix = quant.corr()

corr_matrix['overall'].sort_values(ascending = False)

"""# Imputing to fill in Missing Values"""

imputer = SimpleImputer(strategy = 'median')
q_columns = quant.columns
quant = imputer.fit_transform(quant)
quant = pd.DataFrame(quant, columns = q_columns)

quant

"""# Scaling the Data"""

scaler = StandardScaler()
quant = pd.DataFrame(scaler.fit_transform(quant), columns = quant.columns)
quant

quant.drop('overall', axis = 1, inplace = True)

"""# Process Categorical Data"""

cat = legacy.select_dtypes(include = ['object'])
cat.info()

cat = players.select_dtypes(include = ['object'])
cat.info()

important_cols = ['preferred_foot', 'body_type']
cat.drop(columns = [column for column in cat.columns if column not in important_cols], inplace =True)

cat.info()

"""# One hot encoding"""

cat = pd.get_dummies(cat).astype(int)
cat

"""# Step 4:Model Selection"""

X = pd.concat([cat, quant], axis = 1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=42)

"""# Define and train Linear Regression"""

X_train.dropna(inplace=True)
y_train = y_train[X_train.index] # Update y_train to match the new X_train index
lr_model.fit(X_train, y_train)

"""# Define and train Decision Tree with GridSearchCV"""

dt_model = DecisionTreeRegressor(random_state=42)
dt_params = {
    'max_depth': [3, 5, 7],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}
dt_grid = GridSearchCV(dt_model, dt_params, cv=5, scoring='r2')
dt_grid.fit(X_train, y_train)

"""# Define and train Random Forest with GridSearchCV"""

rf_model = RandomForestRegressor(random_state=42)
rf_params = {
    'n_estimators': [50, 100],
    'max_depth': [3, 5],
    'min_samples_split': [5, 10],
    'min_samples_leaf': [2, 4]
}
rf_model = RandomForestRegressor(random_state=42, n_jobs=-1)
rf_grid = GridSearchCV(rf_model, rf_params, cv=5, scoring='r2', n_jobs=-1)
rf_grid.fit(X_train, y_train)

gb_model = GradientBoostingRegressor(random_state=42)
gb_params = {
    'n_estimators': [50, 100],
    'max_depth': [3, 5],
    'learning_rate': [0.01, 0.1],
    'min_samples_split': [5, 10]
}
gb_grid = GridSearchCV(gb_model, gb_params, cv=5, scoring='r2', n_jobs=-1)
gb_grid.fit(X_train, y_train)

"""# Make predictions using all models"""

# Drop rows with any missing values in X_test
X_test_dropped = X_test.dropna()

# If y_test exists, drop corresponding rows
if 'y_test' in locals():
    y_test_dropped = y_test[X_test_dropped.index]  # Align y_test with dropped X_test

# Predict using the test data with dropped rows
lr_pred = lr_model.predict(X_test_dropped)
dt_pred = dt_grid.best_estimator_.predict(X_test_dropped)
rf_pred = rf_grid.best_estimator_.predict(X_test_dropped)
gb_pred = gb_grid.best_estimator_.predict(X_test_dropped)

"""# Define a function to print performance metrics"""

def print_metrics(name, y_true, y_pred):
    print(f"{name}:")
    print(f"  Mean Absolute Error = {mean_absolute_error(y_true, y_pred):.4f}")
    print(f"  Mean Squared Error = {mean_squared_error(y_true, y_pred):.4f}")
    print(f"  Root Mean Squared Error = {np.sqrt(mean_squared_error(y_true, y_pred)):.4f}")
    print(f"  R2 score = {r2_score(y_true, y_pred):.4f}")
    print()

"""# Print performance metrics for all models"""

print_metrics("Linear Regression", y_test_dropped, lr_pred)
print_metrics("Decision Tree", y_test_dropped, dt_pred)
print_metrics("Random Forest", y_test_dropped, rf_pred)
print_metrics("Gradient Boosting", y_test_dropped, gb_pred)

"""# Print best parameters for models that underwent hyperparameter tuning"""

print("Best parameters for Decision Tree:")
print(dt_grid.best_params_)
print("\nBest parameters for Random Forest:")
print(rf_grid.best_params_)
print("\nBest parameters for Gradient Boosting:")
print(gb_grid.best_params_)

"""# Compare the best scores from GridSearchCV"""

print("\nBest cross-validation scores:")
print(f"Decision Tree: {dt_grid.best_score_:.4f}")
print(f"Random Forest: {rf_grid.best_score_:.4f}")
print(f"Gradient Boosting: {gb_grid.best_score_:.4f}")

""" **Test Using Player's Data**"""

print("All columns in the legacy dataset:")
print(legacy.columns.tolist())

columns_to_drop = ['league_id', 'club_joined_date', 'club_contract_valid_until_year']



z = legacy['overall']

feature_columns = [col for col in legacy.columns if col not in columns_to_drop]

print("\nSelected feature columns:")
print(feature_columns)

X = legacy[feature_columns]
y = legacy['overall'] # Use the column name 'overall' directly

print(f"\nShape of feature matrix X: {X.shape}")
print(f"Shape of target variable y: {y.shape}")

import joblib
joblib.dump(feature_columns, 'selected_features.pkl')

print("\nFeature columns have been saved to 'selected_features.pkl'")

# Load the saved feature columns
feature_columns = joblib.load('selected_features.pkl')

# Use these features for the players_22 dataset
X_22 = players[feature_columns]
y_22 = players['overall']

# When initially scaled your training data:
scaler = StandardScaler()

# Select only numeric columns for scaling
numeric_columns = X.select_dtypes(include=['number']).columns
X_numeric = X[numeric_columns]

X_scaled = pd.DataFrame(scaler.fit_transform(X_numeric), columns=X_numeric.columns)

# Saving the Scaler
import joblib
joblib.dump(scaler, 'scaler.pkl')

scaler = joblib.load('scaler.pkl')

# Select numeric columns in X_22
X_22_numeric = X_22[numeric_columns]

X_22_scaled = pd.DataFrame(scaler.transform(X_22_numeric), columns=X_22_numeric.columns)

""" Step 6: Deploy the Model with Flask"""

best_model = gb_grid.best_estimator_
joblib.dump(best_model, 'fifa_rating_predictor.joblib')

from google.colab import files
files.download('fifa_rating_predictor.joblib')

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = pd.DataFrame(data, index=[0])
    prediction = best_model.predict(features)
    return jsonify({'predicted_rating': prediction[0]})

if __name__ == '__main__':
    app.run(debug=False)

