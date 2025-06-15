"""
1_Model.py

This module contains the Streamlit application for displaying the EPL Match Result Model Explanation.
"""

import streamlit as st


def main():
    """
    Main function to run the Streamlit app.
    """
    # Title and Description
    st.title('⚽️ EPL Match Result Model')
    st.markdown("""
    ## Model Explanation

    The model chosen for predicting the full-time home and away goals in English Premier League matches is the **RandomForestRegressor**. 
    This decision was made after comparing various models and considering several factors:

    1. **Handling of Complex Interactions**:
        - The RandomForestRegressor is capable of capturing complex interactions between features without requiring extensive feature engineering.
        - It can handle both numerical and categorical data effectively, which is crucial for our dataset that includes features like team names, match dates, and venues.

    2. **Robustness to Overfitting**:
        - Random forests are less prone to overfitting compared to individual decision trees. This is achieved by averaging the results of multiple trees, which reduces variance and improves generalization to unseen data.

    3. **Feature Importance**:
        - The model provides insights into feature importance, helping us understand which features contribute most to the predictions. This is valuable for refining the model and making informed decisions based on the results.

    4. **Performance**:
        - The RandomForestRegressor demonstrated strong performance during training and testing phases. It was able to accurately predict the full-time home and away goals, as well as the match results, based on historical data and engineered features.

    5. **Scalability**:
        - The model scales well with large datasets, making it suitable for our extensive dataset that spans multiple seasons and includes detailed match statistics.

    ## Model Workflow

    The workflow for training and using the model involves several steps:

    1. **Data Loading and Cleaning**:
        - Match data is loaded from CSV files, cleaned, and preprocessed to ensure consistency and accuracy.

    2. **Feature Engineering**:
        - New features are added, such as full-time goals, match results, season year, and encoded categorical variables.
        - Rolling averages for shooting statistics and points per game are calculated to capture the form and performance of teams over time.

    3. **Encoding**:
        - Categorical features like team names and venues are encoded using LabelEncoder to convert them into numerical values suitable for the model.

    4. **Model Training**:
        - The dataset is split into training and testing sets.
        - The RandomForestRegressor model is trained on the training set and evaluated on the testing set to ensure its accuracy and generalization.

    5. **Prediction**:
        - The trained model is used to predict future match outcomes based on the input features.
        - Predictions include full-time home and away goals, match results, and points scored based on the accuracy of the predictions.

    The combination of these steps ensures that the model is robust, accurate, and capable of providing valuable insights into match outcomes in the English Premier League.
    """)

    st.link_button(label="GitHub Link with ipynb", url="")


if __name__ == "__main__":
    main()