# Customer-Product-Recommendation-System
This repository contains a comprehensive solution for predicting product recommendations for customers using historical sales data. The project leverages various data preprocessing techniques, feature engineering, and machine learning algorithms to generate personalized product suggestions.

#Table of Contents
Overview
Data Preprocessing
Feature Engineering
Similarity Calculation
Recommendation Generation
Evaluation
Usage
Dependencies
License
Acknowledgments
Overview
The primary objective of this project is to predict top product recommendations for customers by analyzing their historical purchasing behavior. The solution involves several key steps, including data preprocessing, feature engineering, similarity calculation, recommendation generation, and evaluation.

#Data Preprocessing
Loading and Cleaning Data:

Read the data from an Excel file.
Handle missing values by filling them with predefined defaults.
Correct negative revenue values by setting them to zero.
Revenue Imputation:

Replace zero revenue values with the mean revenue for each account using the replace_with_mean_rev() function.
#Feature Engineering
Quarterly Spending:

Extract and aggregate quarterly spending data for each customer.
One-Hot Encoding:

Encode account sizes and quarterly spending data to prepare for similarity calculation.
User-Item Matrix:

Create a matrix where rows represent users and columns represent product types, with values indicating the total revenue spent on each product.
#Similarity Calculation
Use cosine similarity to calculate the similarity between users based on their purchasing behavior.
#Recommendation Generation
Identify Similar Users:

For each user, find the top 20 similar users based on the similarity scores.
Aggregate Product Preferences:

Sum the product-wise spending of the similar users to predict the top products for each user.
#Evaluation
Evaluate the recommendation system by comparing the predicted top products with the actual top products in the test data.
Calculate the Mean Average Precision (mAP) to measure the accuracy of the recommendations.
#Usage
Run the Script:

Execute the script to process the data, generate recommendations, and evaluate the model's performance.
Data File:

Ensure the data file (Prod Recommendation_ Data to share.xlsx) is in the same directory as the script.
Dependencies:

Install the required libraries using the provided requirements.txt file.
#Dependencies
pandas
numpy
scikit-learn
Install the required libraries using:

bash
Copy code
pip install -r requirements.txt
#License
This project is licensed under the MIT License. See the LICENSE file for details.

#Acknowledgments
This project is inspired by the need to enhance personalized product recommendations for improved customer satisfaction using advanced data analysis techniques.
