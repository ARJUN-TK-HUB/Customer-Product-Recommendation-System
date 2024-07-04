import pandas as pd

# Load the data
df = pd.read_excel('Prod Recommendation_ Data to share.xlsx')
print(df)
df['Account Size'] = df['Account Size'].fillna('2-Medium Accounts')

# Convert negative values to 0 and replace 0 values with the mean value corresponding to each Account ID
df.loc[df['Rev'] < 0, 'Rev'] = 0
number_of_zero_rev_rows = (df['Rev'] == 0).sum()
print(number_of_zero_rev_rows)

df['Rev'] = pd.to_numeric(df['Rev'], errors='coerce')  # Coerce errors to NaN

# Calculate mean revenue for each account ID
mean_rev_by_id = df.groupby('Account ID')['Rev'].mean()

def replace_with_mean_rev(row):
    account_id = row['Account ID']
    rev_value = row['Rev']
    if rev_value == 0:
        return mean_rev_by_id.get(account_id, 0)
    else:
        return rev_value

df['Rev'] = df.apply(replace_with_mean_rev, axis=1)

# Handling data up to 2019-Q4 and calculating total quarterly spending
data = pd.read_excel("Prod Recommendation_ Data to share.xlsx")
data['Account Size'] = data['Account Size'].fillna('2-Medium Accounts')
data.loc[data['Rev'] < 0, 'Rev'] = 0
data['Rev'] = pd.to_numeric(data['Rev'], errors='coerce')

mean_rev_by_id = data.groupby('Account ID')['Rev'].mean()
data['Rev'] = data.apply(replace_with_mean_rev, axis=1)

# Extract train data
data = data[data['FISC_QTR_VAL'] != '2020-Q1']
data = data.dropna()
data['Quarter'] = data['FISC_QTR_VAL'].str[-1]
data['Year'] = data['FISC_QTR_VAL'].str[2:4]
print(data)

# Aggregate total amount spent by each user in each quarter over all years
user_quarterly_spending = data.groupby(['Account ID', 'Quarter'])['Rev'].sum().unstack(fill_value=0)
user_quarterly_spending.columns = [f'Total_Q{i}' for i in range(1, 5)]
user_quarterly_spending.reset_index(inplace=True)
print(user_quarterly_spending)

# Hot encoding the quarterly spending
columns_to_replace = ['Total_Q1', 'Total_Q2', 'Total_Q3', 'Total_Q4']
user_quarterly_spending[columns_to_replace] = user_quarterly_spending[columns_to_replace].applymap(lambda x: 1 if x != 0 else 0)
print(user_quarterly_spending)

# Extract test data for 2020-Q1
df_2020 = df[df['FISC_QTR_VAL'] == '2020-Q1']

# Extract only train data (up to 2019-Q4)
df = df[df['FISC_QTR_VAL'] != '2020-Q1']
df = df.dropna()

# Find common customers among train and test data
unique_account_ids_2019 = df['Account ID'].unique().tolist()
unique_account_ids_2020 = df_2020['Account ID'].unique().tolist()
common_ids = list(set(unique_account_ids_2019) & set(unique_account_ids_2020))

df.drop('FISC_QTR_VAL', axis=1)

# One hot encoding of Account Size attribute
unique_account_ids = df['Account ID'].unique()
one_hot_encoded_account_sizes = {}

for account_id in unique_account_ids:
    account_size = df[df['Account ID'] == account_id]['Account Size'].iloc[0]
    one_hot_encoded_account_size = pd.get_dummies([account_size], prefix='Account Size')
    one_hot_encoded_account_size.replace(True, 1, inplace=True)
    one_hot_encoded_account_sizes[account_id] = one_hot_encoded_account_size

account_size_df = pd.concat(one_hot_encoded_account_sizes.values(), keys=one_hot_encoded_account_sizes.keys())
account_size_df.reset_index(inplace=True)
account_size_df.rename(columns={'level_0': 'Account ID'}, inplace=True)
account_size_df.drop(columns=['level_1'], inplace=True)
account_size_df.reset_index(drop=True, inplace=True)
print(account_size_df)

# Create user-item matrix
df = df.groupby(['Account ID', 'Product Type']).agg({'Rev': 'sum'}).reset_index()
print(df)

user_product_matrix = df.pivot_table(values='Rev', index='Account ID', columns='Product Type').fillna(0)
print(user_product_matrix)

# Merge the encoded account size attribute with the user-item matrix
merged_df = pd.merge(user_product_matrix, account_size_df, on='Account ID', how='left')
print(merged_df)

user_product_matrix.fillna(0, inplace=True)
merged_df.fillna(0, inplace=True)
print(merged_df)

# Merge the quarterly spending encoded values to user-item matrix
total_q_values = user_quarterly_spending[['Account ID', 'Total_Q1', 'Total_Q2', 'Total_Q3', 'Total_Q4']]
user_product_matrix.reset_index(inplace=True)
total_q_values.reset_index(inplace=True)

merged_df_with_q = pd.merge(merged_df, total_q_values[['Account ID', 'Total_Q1', 'Total_Q2', 'Total_Q3', 'Total_Q4']], on='Account ID', how='left')
merged_df_with_q.set_index('Account ID', inplace=True)
print(merged_df_with_q)

# Finding similarity matrix using cosine similarity
from sklearn.metrics.pairwise import cosine_similarity

user_similarity_matrix = cosine_similarity(merged_df_with_q)
print(user_similarity_matrix)

# From the user similarity matrix, find the top 20 similar users and predict the top three products
account_product_dict = {}

for id in common_ids:
    user_index = merged_df_with_q.index.get_loc(id)
    user_similarity_scores = user_similarity_matrix[user_index]
    sorted_similarity_indices = user_similarity_scores.argsort()[::-1][0:30]
    similar_user_ids = merged_df_with_q.index[sorted_similarity_indices]
    selected_rows = merged_df_with_q.loc[similar_user_ids]
    column_sums = selected_rows.iloc[:, :72].sum()
    top_3_product_ids = column_sums.nlargest(3).index
    top_3_product_ids = [pid for pid in top_3_product_ids if pid.startswith('P')]
    account_product_dict[id] = top_3_product_ids

print(account_product_dict)

# Finding the actual top 3 products for each user from test data
df_2020 = df_2020.groupby(['Account ID', 'Product Type']).agg({'Rev': 'sum'}).reset_index()
print(df_2020)

user_product_matrix_2020 = df_2020.pivot_table(values='Rev', index='Account ID', columns='Product Type').fillna(0)
print(user_product_matrix_2020)

top_3_items_per_user = {}
zero_count_per_user_item = {}

for index, row in user_product_matrix_2020.iterrows():
    top_3_items = row.sort_values(ascending=False).head(3).index.tolist()
    zero_count_per_user = sum(1 for item in top_3_items if row[item] == 0)
    zero_count_per_user_item[index] = zero_count_per_user
    top_3_items_per_user[index] = top_3_items

print(top_3_items_per_user)

# Finding the number of matches in top 3 predicted and actual top 3 products for each user
matches_per_user = {}

for id in common_ids:
    predicted_products = top_3_items_per_user[id]
    actual_products = account_product_dict[id]
    zero_count = zero_count_per_user_item[id]

    if zero_count == 1:
        predicted_products = predicted_products[:2]
        actual_products = actual_products[:2]
    elif zero_count == 2:
        predicted_products = predicted_products[:1]
        actual_products = actual_products[:1]
    elif zero_count == 3:
        predicted_products = []
        actual_products = []

    matches = sum(1 for product in predicted_products if product in actual_products)
    matches_per_user[id] = matches

print("Number of matches per user ID:")
print(matches_per_user)

# Calculating Mean Average Precision (mAP)
sum_matches = sum(matches_per_user.values())
total_users = len(common_ids)
mean_average_precision = sum_matches / (3 * total_users)
print(mean_average_precision)
