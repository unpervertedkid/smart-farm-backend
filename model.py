import pandas as pd 
import matplotlib.pyplot as plt 
import pickle
import numpy as np 

from sklearn.model_selection import train_test_split
import sklearn.metrics as metrics 
from sklearn.linear_model import LogisticRegression
import seaborn as sns

PATH = 'data/Crop_recommendation.csv'

# Load the csv file data into the data variable using pandas
data = pd.read_csv(PATH)


# Print the first five rows of the dataset to get to know what types of values are given 
data.head()

# Display info about the datatype , NULL type of the columns of the data
data.info()

# Descriptive analysis
data.describe()

# Exploratory Data analysis

# Display the unique input data labels
data['label'].unique()

# Check whether the classes provided in the dataset are balanced by counting each unique label
data['label'].value_counts()

# Find the distribution of the data input features
plt.rcParams['figure.figsize'] = (10,10)
plt.rcParams['figure.dpi'] = 60

features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

for i, feature in enumerate(features):
    plt.subplot(4,2,i+1)
    sns.distplot(data[feature], color='greenyellow')
    if i < 3:
        plt.title(f'Ration of {feature}', fontsize = 12)
    else:
        plt.title(f'Distribution of {feature}', fontsize=12)

    plt.tight_layout()
    plt.grid()
    

# Feature distribution for different crops
sns.pairplot(data, hue='label')

# Find correlation between features
# Select only numeric columns
numeric_data = data.select_dtypes(include=[np.number])

fig, ax = plt.subplots(1, 1, figsize=(15, 9))
sns.heatmap(numeric_data.corr(),
			annot=True,
			cmap='viridis')
ax.set(xlabel='features')
ax.set(ylabel='features')

plt.title('Correlation between different features',
		fontsize=15,
		c='black')
plt.show()


# Separate input and ouput variables
features = data[['N', 'P', 'K', 'temperature',
				'humidity', 'ph', 'rainfall']]

labels = data['label']


# Model training

X_train, X_test,\
	Y_train, Y_test = train_test_split(features,
									labels,
									test_size=0.2,
									random_state=42)


# Pass the training set into the
# LogisticRegression model from Sklearn
LogisticRegressionModel = LogisticRegression(random_state=42)\
.fit(X_train, Y_train)

# Predict the values for the test dataset
predicted_values = LogisticRegressionModel.predict(X_test)

# Measure the accuracy of the test 
# set using accuracy_score metric
accuracy = metrics.accuracy_score(Y_test,
								predicted_values)


# Print out the accuracy of the model
print("Logistic Regression Accuracy: ", accuracy)

# Print the accuracy for each crop
# Get detail metrics 
print(metrics.classification_report(Y_test,
									predicted_values))

# Save the model
filename = 'CropPrediction.pkl'
filepath = './models'

pickle.dump(LogisticRegressionModel, open(filepath + filename, 'wb'))

