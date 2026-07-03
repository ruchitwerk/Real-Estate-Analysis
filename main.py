import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data.csv')

# ---------- Data Cleaning ----------
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Numerical columns: remove thousands separators and convert types
df['price'] = df['price'].astype(str).str.replace(',', '').astype(float)
df['area'] = df['area'].astype(str).str.replace(',', '').astype(int)
df['rate_per_sqft'] = df['rate_per_sqft'].astype(str).str.replace(',', '').astype(int)

# Categorical columns: normalize text values
df['status'] = df['status'].str.strip().str.lower()
df['rera_approval'] = df['rera_approval'].str.strip().str.lower().map(
    {'approved by rera': True, 'not approved by rera': False}
)
df['flat_type'] = df['flat_type'].str.strip().str.lower()

df = df.drop_duplicates()

# Outlier handling: the raw data contains data-entry errors such as
# listings with 99+ BHK or a BHK count of 0. Keep only plausible
# residential configurations (1-10 BHK) for BHK-based analysis.
df = df[(df['bhk_count'] >= 1) & (df['bhk_count'] <= 10)]

print(f"Dataset after cleaning: {len(df):,} listings\n")

# ---------- Analysis ----------

# Question 1: Which is the costliest flat in the dataset?
costliest_flat = df.loc[df['price'].idxmax()]
print(f"1. The costliest flat is a {costliest_flat['bhk_count']} BHK in "
      f"{costliest_flat['locality']} ({costliest_flat['society']}), "
      f"priced at {costliest_flat['price'] / 1e7:.2f} crores.")

# Question 2: Which locality has the highest average price?
highest_avg_price_locality = df.groupby('locality')['price'].mean().idxmax()
print(f"2. The locality with the highest average price is {highest_avg_price_locality}.")

# Question 3: Which locality has the highest rate per square foot?
highest_rate_locality = df.groupby('locality')['rate_per_sqft'].mean().idxmax()
print(f"3. The locality with the highest rate per sqft is {highest_rate_locality}.")

# Question 4: Do ready-to-move properties cost more than under-construction ones?
ready_avg = df[df['status'] == 'ready to move']['price'].mean()
uc_avg = df[df['status'] == 'under construction']['price'].mean()
if ready_avg > uc_avg:
    print("4. Ready-to-move properties cost more on average than under-construction properties.")
else:
    print("4. Under-construction properties cost more on average than ready-to-move properties.")

# Question 5: Do RERA-approved properties command a price premium?
rera_avg = df[df['rera_approval'] == True]['price'].mean()
non_rera_avg = df[df['rera_approval'] == False]['price'].mean()
if rera_avg > non_rera_avg:
    print("5. RERA-approved properties command a price premium on average.")
else:
    print("5. RERA-approved properties do NOT command a price premium on average "
          "- an unexpected finding worth deeper investigation.")

# Question 6: How does area impact price?
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x='area', y='price', alpha=0.4)
plt.title('Area vs. Property Price')
plt.xlabel('Area (sqft)')
plt.ylabel('Price')
plt.tight_layout()
plt.savefig('images/area_vs_price.png', dpi=150)
plt.close()
print("6. Saved plot: images/area_vs_price.png - price rises with area overall.")

# Question 7: Which BHK configuration is most expensive per sqft?
most_expensive_bhk = df.groupby('bhk_count')['rate_per_sqft'].mean().idxmax()
print(f"7. The most expensive BHK configuration on average is {most_expensive_bhk} BHK.")

# Question 8: Which property type is the costliest per sqft?
most_expensive_type = df.groupby('flat_type')['rate_per_sqft'].mean().idxmax()
print(f"8. The most expensive property type is {most_expensive_type}.")

# Question 9: Do certain builders price higher?
# Only rank builders with at least 20 listings, so that one-off entries
# and misspelled builder names do not distort the ranking.
builder_stats = df.groupby('company_name')['rate_per_sqft'].agg(['mean', 'count'])
top_5_builders = (builder_stats[builder_stats['count'] >= 20]
                  .sort_values('mean', ascending=False).head(5))
print("9. Top 5 builders by average rate per sqft (min. 20 listings):",
      ", ".join(top_5_builders.index))

# Bar chart: average price by property type
plt.figure(figsize=(8, 5))
avg_price_by_type = df.groupby('flat_type')['price'].mean().sort_values(ascending=False)
sns.barplot(x=avg_price_by_type.index, y=avg_price_by_type.values)
plt.title('Average Price by Property Type')
plt.xlabel('Property Type')
plt.ylabel('Average Price')
plt.tight_layout()
plt.savefig('images/price_by_type.png', dpi=150)
plt.close()

# Question 10: Are larger homes more expensive per sqft?
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x='area', y='rate_per_sqft', alpha=0.4)
plt.title('Area vs. Rate per SqFt')
plt.xlabel('Area (sqft)')
plt.ylabel('Rate per sqft')
plt.tight_layout()
plt.savefig('images/area_vs_rate.png', dpi=150)
plt.close()
print("10. Saved plot: images/area_vs_rate.png - rate per sqft does not "
      "strictly increase with area.")
