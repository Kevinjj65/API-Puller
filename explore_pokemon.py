import pandas as pd
import matplotlib.pyplot as plt
df=pd.read_csv('pokemon_data.csv')
print(df.head())
print(df.describe())
df.info()
print(df.isna().sum())
#highest base experience
print(df.sort_values('base_experience',ascending=False).head(1))
#average weight across all 100 pokemons
print(f"Avg weight is {df['weight'].mean()}")
#height greater than 10
print(f"Number of Pokémon with height > 10: {len(df[df['height']>10])}")

#histogram of base experience
plt.hist(df['base_experience'])
plt.xlabel('Base Experience')
plt.ylabel('Frequency')
plt.title('Distribution of Base Experience')
plt.show()

#sorting pokemons by height
df['height_group'] = pd.cut(df['height'], bins=[0, 10, 20, 100], labels=['short', 'medium', 'tall'])

#bargraph for height group
df['height_group'].value_counts().plot(kind='bar')
plt.title("Pokemon by Height Group")
plt.xlabel("Height Group")
plt.ylabel("Count")
plt.show()

#scatter plot for height vs weight
plt.scatter(df['height'], df['weight'])
plt.title("Height vs Weight")
plt.xlabel("Height")
plt.ylabel("Weight")
plt.show()