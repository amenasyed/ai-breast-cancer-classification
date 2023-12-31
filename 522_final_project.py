# -*- coding: utf-8 -*-
"""522_Final_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uk-i0jJBvDF9Wwa_i4F0dtYQSSZlXYri

**Dataset Cleaning**
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score

df = pd.read_csv('breastcancerdata.csv')
df.info()

# Remove 'id' and 'Unnamed:32' column as they don't provide useful information
df.drop(axis=1, columns=['id','Unnamed: 32'], inplace=True)
print(df.head())

df.describe()

plt.figure(figsize=(30,15))
sns.heatmap(df.corr(), annot=True)
plt.show()

# Split target from data and assign malignant to 1 and benign to -1 for classification
Target = df['diagnosis']
df.drop(axis=1, columns=['diagnosis'], inplace=True)
Target.replace(to_replace='M', value=1, inplace=True)
Target.replace(to_replace='B', value=-1, inplace=True)

num_malignant = np.count_nonzero(Target == 1)
print('Number of Malignant Observations:', num_malignant)
num_benign = np.count_nonzero(Target == -1)
print('Number of Benign Observations:', num_benign)

fig = plt.figure(figsize = (10, 10))

value = [num_malignant, num_benign]
bars = ("Malignant", "Benign")

# Create bars with different colors
plt.bar(np.arange(len(bars)), value, color=['red', 'black'])
plt.xticks(np.arange(len(bars)), bars)
plt.xlabel("Diagnosis Type")
plt.ylabel("Diagnosis Count")
plt.title("Diagnosis Outcome")
plt.show()


# This technically reduces accuracy slightly but might be worth it for data compression
# redundant_features = ['radius_mean', 'area_worst', 'area_se']
# df.drop(axis=1, columns=redundant_features, inplace=True)

"""**Data Visualization**"""

#PairPlot for first 9 features
pair_plot_df = df.join(Target)
columns = ['radius_mean', 'texture_mean', 'perimeter_mean',
       'area_mean', 'smoothness_mean', 'compactness_mean', 'concavity_mean',
       'concave points_mean', 'symmetry_mean','diagnosis']

pair_plot = sns.pairplot(data=pair_plot_df[columns],hue='diagnosis',palette='viridis')

"""**Splitting Data Set and Standardization**"""

from collections import Counter
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(df, Target, test_size=0.25, random_state=0)

DataMean = X_train.mean()
DataStdDev = X_train.std()

# Standardize data
StandardizedTrainData = (X_train - DataMean) / DataStdDev
StandardizedTestData = (X_test - DataMean) / DataStdDev

# Resample using SMOTE
smote = SMOTE()
X_train_resampled, y_train_resampled = smote.fit_resample(StandardizedTrainData, y_train)

# Compare the two classes
print(Counter(y_train))
print(Counter(y_train_resampled))

from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

model = svm.SVC(C=10)

# Calculate cross-validation accuracy for 10 fold CV
scores = cross_val_score(model, X_train, y_train, cv=10)

print("Scores = ", scores)

model.fit(StandardizedTrainData, y_train)
preds = model.predict(StandardizedTestData)
preds_train = model.predict(StandardizedTrainData)

print("Train Accuracy:", accuracy_score(y_train, preds_train))
print("Test Accuracy:", accuracy_score(y_test, preds))

cm = ConfusionMatrixDisplay(confusion_matrix(y_test, preds), display_labels = [False, True]).plot()
plt.show()
plt.savefig('confusion-matrix.png')

# With SMOTE
smote_model = svm.SVC(C=10)

# Calculate cross-validation accuracy for 10 fold CV
scores_smote = cross_val_score(smote_model, X_train, y_train, cv=10)

print("Scores = ", scores_smote)

smote_model.fit(X_train_resampled, y_train_resampled)
smote_preds = model.predict(StandardizedTestData)

print("Test Accuracy:", accuracy_score(y_test, smote_preds))

cm = ConfusionMatrixDisplay(confusion_matrix(y_test, smote_preds), display_labels = [False, True]).plot()
plt.show()

"""**PCA On Wisconsin Dataset**"""

# Making Covariance Matrix
covariance_matrix = np.cov(StandardizedTrainData.T)

# Getting the EigenVectors and the EigenValues
eigen_values, eigen_vectors = np.linalg.eig(covariance_matrix)

# Higher explained variance indicates model is capturing data structure better
explained_var = []
pc = []

var_const= 0
for i in range(len((eigen_values/(np.sum(eigen_values))*100))):
    var_const = var_const + np.around((eigen_values[i]/(np.sum(eigen_values))*100),3)
    while var_const < 100:
        explained_var.append(var_const)
        pc.append(i)
        print('At', i,'PC,', 'Explained Variance is',var_const)
        break

# We want to retain the highest amount of information while reducing redundancy

# Choosing the number of principal components
plt.plot(pc, explained_var)
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance')
plt.title('Choosing the Number of Principal Components')
plt.show()

# Index of sorted eigvalues in descending order
sort_idx = np.argsort(eigen_values)[::-1]

# Sort eigenvalues and eigenvectors in descending order
eigen_values, eigen_vectors = eigen_values[sort_idx], eigen_vectors.T[sort_idx]

# Using matrix multiplication, multiplying the training data with eigenvectors to create new projections
n_components = 2
PCA_eigen_values = eigen_vectors[:n_components].real.T

PCA = StandardizedTrainData @ PCA_eigen_values
PCA['Target']=y_train.values

# Plot processed PCA data (top 2 principal components)
sns.scatterplot(data= PCA, x=PCA[0],y=PCA[1], hue=PCA['Target'])
plt.title('PCA Scatterplot For Top 2 Principal Components')

plt.xlabel('PC1')
plt.ylabel('PC2')
plt.show()

"""**LDA on Wisconsin Dataset**"""

from scipy import linalg

LDAStandardizedTrainData = np.array(StandardizedTrainData)

# Initialize
n_classes = 2 # either B or M
n_components = LDAStandardizedTrainData.shape[1]

n = np.zeros(n_classes).astype(int)
S = np.zeros(((n_classes, n_components, n_components)))
M = np.mean(LDAStandardizedTrainData, axis=0)
Sw = np.zeros((n_components, n_components))
Sb = Sw
C = np.zeros((n_classes, n_components))

for j in np.unique(y_train):
    Xj = LDAStandardizedTrainData[y_train == j, :] # samples in class j
    n[j] = (Xj.shape[0]) # number of samples in class j
    C[j,:] = np.mean(Xj, axis = 0)

    for i in range(n[j]):
      S[j,:,:] = S[j] + (Xj[i,:] - C[j,:])[np.newaxis].T @ (Xj[i,:] - C[j,:][np.newaxis]) # matmul for class scatter
    Sw = Sw + S[j,:,:];
    Sb = Sb + n[j]*(C[j,:] - M)[np.newaxis].T @ (C[j,:] - M)[np.newaxis]

eigen_values, eigen_vectors =linalg.eig(np.linalg.inv(Sw)@Sb)
for i in range(len(eigen_values)):
  # index of sorted eigvalues in descending order
  sort_idx = np.argsort(eigen_values)[::-1]
  # sorted eigenvalues and eigenvectors
  eigen_values, eigen_vectors = eigen_values[sort_idx], eigen_vectors[sort_idx]

# Using matrix multiplication, multiplying the training data with eigenvectors to create new projections
n_components = 2
LDA_eigen_values = eigen_vectors[:n_components].real.T

LDA = LDAStandardizedTrainData @ LDA_eigen_values

# Plot processed LDA data
plt.plot(LDA[y_train==-1,0],LDA[y_train==-1,1],'.')
plt.plot(LDA[y_train==1,0],LDA[y_train==1,1],'o')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('LDA Scatterplot For Top 2 Principal Components ')
plt.legend(["-1" , "1"], ncol = 1 , loc = "lower right", title='Target')
plt.show()

"""**Grid Search on Standardized, PCA and LDA Data**"""

from sklearn import svm
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
import time

# Using SGD Classifier
model = SGDClassifier(loss = 'hinge', penalty='l1', alpha=1e-05, max_iter=1000, learning_rate='constant', eta0=0.0001, random_state = 3) # You will need to tune the LR and Regularization

# Make a pipeline of steps
clf = Pipeline(steps=[("model", model)])

# Grid search
param_grid = {'model__alpha': [0.00001, 0.0001, 0.001, 0.1, 1, 10, 100, 1000],
              'model__eta0': [100, 10, 1, 0.1, 0.01, 0.001, 0.0001, 0.00001],
              'model__penalty': ['l1', 'l2'],
              'model__learning_rate': ['constant', 'adaptive']
              }
grid = GridSearchCV(clf, param_grid=param_grid, refit = True, verbose=1)

# STANDARDIZED DATA
time_start = time.time()
grid.fit(StandardizedTrainData,y_train) # fit on the standardized original data
time_grid = time.time() - time_start
print("Time for Grid ", time_grid)

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on original= ", grid.best_score_)
print("Best set of parameters on original = ", grid.best_params_)

# Predictions on standardized test data
grid_predictions_stand = grid.predict(StandardizedTestData)

print(classification_report(y_test, grid_predictions_stand))

# PCA DATA
x_train_pca = StandardizedTrainData @ PCA_eigen_values
x_test_pca = StandardizedTestData @ PCA_eigen_values

# Resampled (Commented out because it makes negligible difference)
# X_train_PCA_resampled, y_train_resampled = smote.fit_resample(x_train_pca, y_train)
# grid.fit (X_train_PCA_resampled, y_train_resampled) # fit on standardized_pca_data

grid.fit(x_train_pca, y_train) # fit on standardized pca data

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on PCA = ", grid.best_score_)
print("Best set of parameters on PCA = ", grid.best_params_)

grid_predictions_pca = grid.predict(x_test_pca)
print(classification_report(y_test, grid_predictions_pca))

# LDA DATA
x_train_lda = StandardizedTrainData @ LDA_eigen_values
x_test_lda = StandardizedTestData @ LDA_eigen_values

grid.fit(x_train_lda, y_train) # fit on standardized lda data

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on LDA = ", grid.best_score_)
print("Best set of parameters on LDA = ", grid.best_params_)

grid_predictions_lda = grid.predict(x_test_lda)
print(classification_report(y_test, grid_predictions_lda))

"""**Random Search on Standardized, PCA and LDA Data**"""

from scipy.stats import uniform
# Create model instance
model = SGDClassifier()

clf = Pipeline(steps=[("model", model)])

param_grid = {'model__alpha': uniform(loc=0, scale=1),
              'model__eta0': uniform(loc=0, scale=1),
              'model__penalty': ['l1', 'l2'],
              'model__learning_rate': ['constant', 'adaptive']
              }

grid = RandomizedSearchCV(clf, param_grid, n_iter = 20, refit = True, verbose=1)

# STANDARDIZED DATA
time_start = time.time()
grid.fit(StandardizedTrainData,y_train) # fit on the standardized original data
time_random = time.time() - time_start
print("Time for Random ", time_random)

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on original= ", grid.best_score_)
print("Best set of parameters on original = ", grid.best_params_)

grid_predictions_stand = grid.predict(StandardizedTestData)
print(classification_report(y_test, grid_predictions_stand))

# PCA DATA
grid.fit(x_train_pca, y_train) # fit on standardized pca data

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on PCA = ", grid.best_score_)
print("Best set of parameters on PCA = ", grid.best_params_)

grid_predictions_pca = grid.predict(x_test_pca)
print(classification_report(y_test, grid_predictions_pca))

# LDA DATA
grid.fit(x_train_lda, y_train) # fit on standardized lda data

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on LDA = ", grid.best_score_)
print("Best set of parameters on LDA = ", grid.best_params_)

grid_predictions_lda = grid.predict(x_test_lda)
print(classification_report(y_test, grid_predictions_lda))

"""**Bayesian Parameter Tuning on Standardized, PCA and LDA Data**"""

!sudo pip install scikit-optimize
from skopt import BayesSearchCV
from skopt.space import Real, Categorical

# Create model instance
model = SGDClassifier()

clf = Pipeline(steps=[("model", model)])

param_grid = {'model__alpha': Real(1e-6, 1e+3, prior='log-uniform'),
              'model__eta0': Real(1e-6, 1e+2, prior='log-uniform'),
              'model__penalty': Categorical(['l1', 'l2']),
              'model__learning_rate': Categorical(['constant', 'adaptive'])
              }

grid = BayesSearchCV(clf, param_grid, n_iter = 20, refit = True, verbose=1)

time_start = time.time()

# STANDARDIZED DATA
grid.fit(StandardizedTrainData,y_train) # fit on the standardized original data
time_bayesian = time.time() - time_start
print("Time for Bayesian ", time_bayesian)

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on original= ", grid.best_score_)
print("Best set of parameters on original = ", grid.best_params_)

grid_predictions_stand = grid.predict(StandardizedTestData)
print(classification_report(y_test, grid_predictions_stand))

# PCA DATA
grid.fit(x_train_pca, y_train) # fit on standardized pca data

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on PCA = ", grid.best_score_)
print("Best set of parameters on PCA = ", grid.best_params_)

grid_predictions_pca = grid.predict(x_test_pca)
print(classification_report(y_test, grid_predictions_pca))

# LDA DATA
grid.fit(x_train_lda, y_train) # fit on standardized lda data

# Mean cross-validated score of the best estimator
print("Mean CV accuracy of the best set of parameters on LDA = ", grid.best_score_)
print("Best set of parameters on LDA = ", grid.best_params_)

grid_predictions_lda = grid.predict(x_test_lda)
print(classification_report(y_test, grid_predictions_lda))

"""**SVM-OVO on PCA Dataset**"""

from itertools import combinations
from scipy.stats import mode
from sklearn.metrics import accuracy_score

training_data = []
y=y_train.to_numpy()
PCA_data = PCA.drop(columns=['Target']).to_numpy()
X_test_PCA=StandardizedTestData @ PCA_eigen_values


class_pairs = list(combinations(set(y), 2))
for class_pair in class_pairs:
    class_mask = np.where((y == class_pair[0]) | (y == class_pair[1]))
    y_i = np.where(y[class_mask] == class_pair[0], 1, -1)
    training_data.append((PCA_data[class_mask], y_i))

classifiers = []
for data in training_data:
    clf = SGDClassifier(loss = 'hinge', penalty='l1', alpha=1e-05, max_iter=1000, learning_rate='constant', eta0=0.0001, random_state = 3)#svm.SVC(kernel='linear', C=1000, decision_function_shape='ovo') #EDIT with optimized parameters
    clf.fit(data[0], data[1]) # fit the SVM model for each binary classifier on the X and y for each pair of classifiers
    classifiers.append(clf)

def predict_class(X, classifiers, class_pairs):
    predictions = np.zeros((X.shape[0], len(classifiers)))
    for idx, clf in enumerate(classifiers):
        class_pair = class_pairs[idx]
        prediction = clf.predict(X)
        predictions[:, idx] = np.where(prediction == 1, class_pair[0], class_pair[1])
    return mode(predictions, axis=1)[0].ravel().astype(int), predictions # use mode to return the frequently repeated number in predictions i.e. the highest voting class

#training accuracy
Z_train, _ = predict_class(PCA_data, classifiers, class_pairs)
print("Training accuracy using {}:".format('linear SVM'), accuracy_score(Z_train, y_train))

#training accuracy
Z_test, _ = predict_class(X_test_PCA, classifiers, class_pairs)
print("Testing accuracy using {}:".format('linear SVM'), accuracy_score(Z_test, y_test))

#Print OVO graph
y_1 = np.where(y == -1, 1, -1)
y_2 = np.where(y == 1, 1, -1)

# create a mesh to plot in
h = 0.02  # step size in the mesh
x_min, x_max = PCA_data[:, 0].min() - 1, PCA_data[:, 0].max() + 1
y_min, y_max = PCA_data[:, 1].min() - 1, PCA_data[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                    np.arange(y_min, y_max, h))

Z,_ = predict_class(np.c_[xx.ravel(), yy.ravel()], classifiers, class_pairs)

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm, alpha=0.5)

# Plot also the training points
plt.scatter(PCA_data[y_1==1, 0], PCA_data[y_1==1, 1], s=100, marker='X', c='blue', label ='Benign')
plt.scatter(PCA_data[y_2==1, 0], PCA_data[y_2==1, 1], s=100, marker='^', c='black', label ='Malignant')

#Plot the test point and have the colours different to see each class
benign_indices = np.where(y_test == -1)[0]
malignant_indices = np.where(y_test == 1)[0]

PCA_column_one = X_test_PCA.to_numpy()[:, 0]
PCA_column_two = X_test_PCA.to_numpy()[:, 1]
plt.scatter(PCA_column_one[benign_indices], PCA_column_two[benign_indices], s=50, marker='s', c='hotpink', label ='Test Points (Benign)')
plt.scatter(PCA_column_one[malignant_indices], PCA_column_two[malignant_indices], s=50, marker='s', c='red', label ='Test Points (Malignant)')

plt.xlabel('x1')
plt.ylabel('x2')
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.title('SVC with OVO')
plt.legend()

plt.legend()

plt.show()

"""**SVM-OVA on PCA Dataset**"""

Y = [y_1, y_2]
PCA_data = PCA.drop(columns=['Target']).to_numpy()
X_test_PCA=StandardizedTestData @ PCA_eigen_values

classifiers = []
for y_i in Y:
    clf = SGDClassifier(loss = 'hinge', penalty='l1', alpha=1e-05, max_iter=1000, learning_rate='constant', eta0=0.0001, random_state = 3)#svm.SVC(kernel='linear', C=11, decision_function_shape='ovr')
    clf.fit(PCA_data, y_i) # fit the SVM model for each binary classifier
    classifiers.append(clf)

def predict_class(X, classifiers):
    predictions = np.zeros((X.shape[0], len(classifiers)))
    for idx, clf in enumerate(classifiers):
        predictions[:, idx] = clf.decision_function(X) # the score i.e the signed distance to the seperating hyperplane w^T.X + b = 0
    # return the argmax of the score function
    return np.argmax(predictions, axis=1)

#training accuracy
Z_train= predict_class(PCA_data, classifiers)
y_train_zero_one = y_train.replace({-1:0})
y_test_zero_one = y_test.replace({-1:0})

print("Training accuracy using {}:".format('linear SVM'), accuracy_score(Z_train, y_train_zero_one))

#training accuracy
Z_test= predict_class(X_test_PCA, classifiers)
print("Testing accuracy using {}:".format('linear SVM'), accuracy_score(Z_test, y_test_zero_one))

# create a mesh to plot in
h = 0.02  # step size in the mesh
x_min, x_max = PCA_data[:, 0].min() - 1, PCA_data[:, 0].max() + 1
y_min, y_max = PCA_data[:, 1].min() - 1, PCA_data[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                    np.arange(y_min, y_max, h))

Z = predict_class(np.c_[xx.ravel(), yy.ravel()], classifiers)

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm, alpha=0.5)

# Plot also the training points
plt.scatter(PCA_data[y_1==1, 0], PCA_data[y_1==1, 1], s=100, marker='X', c='blue', label ='Benign')
plt.scatter(PCA_data[y_2==1, 0], PCA_data[y_2==1, 1], s=100, marker='^', c='black', label ='Malignant')

plt.xlabel('x1')
plt.ylabel('x2')
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.title('SVC with OVA')
plt.legend()

#Plot the test points predictions
PCA_column_one = X_test_PCA.to_numpy()[:, 0]
PCA_column_two = X_test_PCA.to_numpy()[:, 1]
plt.scatter(PCA_column_one[benign_indices], PCA_column_two[benign_indices], s=50, marker='s', c='hotpink', label ='Test Points (Benign)')
plt.scatter(PCA_column_one[malignant_indices], PCA_column_two[malignant_indices], s=50, marker='s', c='red', label ='Test Points (Malignant)')

plt.legend()

plt.show()

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

pca = PCA(n_components=6)

X_train_pca = pca.fit_transform(StandardizedTrainData)
X_test_pca = pca.transform(StandardizedTestData)

param_grid = {'C': [0.01, 0.1, 0.5, 1, 10, 100],
              'gamma': [1, 0.75, 0.5, 0.25, 0.1, 0.01, 0.001],
              'kernel': ['rbf', 'poly', 'linear']}

grid = GridSearchCV(SVC(), param_grid, refit=True, verbose=1, cv=5)
grid.fit(X_train_pca, y_train)
best_params = grid.best_params_
print(f"Best params: {best_params}")

svm_clf = SVC(**best_params, verbose=True)

# Calculate cross-validation accuracy for 10 fold CV
scores = cross_val_score(svm_clf, X_train_pca, y_train, cv=10)

print("Scores = ", scores)
print("%0.2f accuracy with a standard deviation of %0.2f" % (scores.mean(), scores.std()))


svm_clf.fit(X_train_pca, y_train)

pred = svm_clf.predict(X_train_pca)
clf_report = pd.DataFrame(classification_report(y_train, pred, output_dict=True))
print("Train Result:")
print(f"Accuracy Score: {accuracy_score(y_train, pred) * 100:.2f}%")
print(f"CLASSIFICATION REPORT:\n{clf_report}")

pred = svm_clf.predict(X_test_pca)
clf_report = pd.DataFrame(classification_report(y_test, pred, output_dict=True))
print("Test Result:")
print(f"Accuracy Score: {accuracy_score(y_test, pred) * 100:.2f}%")
print(f"CLASSIFICATION REPORT:\n{clf_report}")

"""**Linear Classification on Standardized Dataset**"""

from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score

pca = PCA(n_components=6)

X_train_pca = pca.fit_transform(StandardizedTrainData)
X_test_pca = pca.transform(StandardizedTestData)

# initializing variables
feature_1 = X_train_pca[:,0]
feature_2 = X_train_pca[:,1]
feature_3 = X_train_pca[:,2]
feature_4 = X_train_pca[:,3]
feature_5 = X_train_pca[:,4]
feature_6 = X_train_pca[:,5]
Y = y_train

# intializing the weights
w1 = 0.0001
w2 = 0.0001
w3 = 0.0001
w4 = 0.0001
w5 = 0.0001
w6 = 0.0001
alpha = 0.01 # the learning rate
epochs = 500 # the number of iterations
n = len(feature_1)

for i in range(epochs):
    score = w1*feature_1 + w2*feature_2 + w3*feature_3 + w4*feature_4 + w5*feature_5 + w6*feature_6
    Y_pred = np.sign(score)
    training_data = np.vstack((feature_1, feature_2, feature_3, feature_4, feature_5, feature_6, Y)).T
    d_w1 = (1/n) * sum(-x1 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w1
    d_w2 = (1/n) * sum(-x2 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w2
    d_w3 = (1/n) * sum(-x3 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w1
    d_w4 = (1/n) * sum(-x4 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w2
    d_w5 = (1/n) * sum(-x5 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w1
    d_w6 = (1/n) * sum(-x6 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w2
    w1 = w1 - alpha * d_w1  # update w1
    w2 = w2 - alpha * d_w2  # update w2
    w3 = w3 - alpha * d_w3  # update w1
    w4 = w4 - alpha * d_w4  # update w2
    w5 = w5 - alpha * d_w5  # update w1
    w6 = w6 - alpha * d_w6  # update w2

    if(i%1000==0):
      print(f'epoch {i}: w = {w1, w2}, gradientF = {d_w1, d_w2}')

print (f'The final trained weights are w1 = {w1} and w2 = {w2}')

# Plotting the predictions
score_train = w1*feature_1 + w2*feature_2 + w3*feature_3 + w4*feature_4 + w5*feature_5 + w6*feature_6
Y_predicted = np.sign(w1*feature_1 + w2*feature_2 + w3*feature_3 + w4*feature_4 + w5*feature_5 + w6*feature_6)

plt.scatter(feature_1, feature_2, c=Y_predicted)
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Linear Classification Using Gradient Descent on Standardized Dataset')
plt.show()

# Testing predictor on test data
# initializing variables
feature_1_test = X_test_pca[:,0]
feature_2_test = X_test_pca[:,1]
feature_3_test = X_test_pca[:,2]
feature_4_test = X_test_pca[:,3]
feature_5_test = X_test_pca[:,4]
feature_6_test = X_test_pca[:,5]
Y_train = y_train
Y_test = y_test

# check accuracy of predictor
accuracy_train = (accuracy_score(Y_predicted, Y_train))*100
print(f'The training accuracy is {accuracy_train}%')


score_test = w1*feature_1_test + w2*feature_2_test + w3*feature_3_test + w4*feature_4_test + w5*feature_5_test + w6*feature_6_test
Y_predicted_test = np.sign(w1*feature_1_test + w2*feature_2_test + w3*feature_3_test + w4*feature_4_test + w5*feature_5_test + w6*feature_6_test)

accuracy_test = (accuracy_score(Y_predicted_test, Y_test))*100
print(f'The testing accuracy is {accuracy_test}%')

# Linear Classification With SMOTE
from sklearn.metrics import accuracy_score

# initializing variables
pca = PCA(n_components=6)

X_train_pca_resampled = pca.fit_transform(X_train_resampled)
X_test_pca = pca.transform(StandardizedTestData)
Y = y_train_resampled

# initializing variables
feature_1 = X_train_pca_resampled[:,0]
feature_2 = X_train_pca_resampled[:,1]
feature_3 = X_train_pca_resampled[:,2]
feature_4 = X_train_pca_resampled[:,3]
feature_5 = X_train_pca_resampled[:,4]
feature_6 = X_train_pca_resampled[:,5]

# intializing the weights
w1 = 0.0001
w2 = 0.0001
w3 = 0.0001
w4 = 0.0001
w5 = 0.0001
w6 = 0.0001
alpha = 0.01 # the learning rate
epochs = 500 # the number of iterations
n = len(feature_1)

for i in range(epochs):
    score = w1*feature_1 + w2*feature_2 + w3*feature_3 + w4*feature_4 + w5*feature_5 + w6*feature_6
    Y_pred = np.sign(score)
    training_data = np.vstack((feature_1, feature_2, feature_3, feature_4, feature_5, feature_6, Y)).T
    d_w1 = (1/n) * sum(-x1 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w1
    d_w2 = (1/n) * sum(-x2 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w2
    d_w3 = (1/n) * sum(-x3 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w1
    d_w4 = (1/n) * sum(-x4 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w2
    d_w5 = (1/n) * sum(-x5 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w1
    d_w6 = (1/n) * sum(-x6 * y if 1 - (w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5 + w6*x6) * y > 0 else 0 for x1, x2, x3, x4, x5, x6, y in training_data) # gradient wrt w2
    w1 = w1 - alpha * d_w1  # update w1
    w2 = w2 - alpha * d_w2  # update w2
    w3 = w3 - alpha * d_w3  # update w1
    w4 = w4 - alpha * d_w4  # update w2
    w5 = w5 - alpha * d_w5  # update w1
    w6 = w6 - alpha * d_w6  # update w2

    if(i%1000==0):
      print(f'epoch {i}: w = {w1, w2}, gradientF = {d_w1, d_w2}')

print (f'The final trained weights are w1 = {w1} and w2 = {w2}')

# Plotting the predictions
score_train = w1*feature_1 + w2*feature_2 + w3*feature_3 + w4*feature_4 + w5*feature_5 + w6*feature_6
Y_predicted = np.sign(w1*feature_1 + w2*feature_2 + w3*feature_3 + w4*feature_4 + w5*feature_5 + w6*feature_6)

plt.scatter(feature_1, feature_2, c=Y_predicted)
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Linear Classification Using Gradient Descent on Standardized Dataset')
plt.show()

# Testing predictor on test data
# initializing variables
feature_1_test = X_test_pca[:,0]
feature_2_test = X_test_pca[:,1]
feature_3_test = X_test_pca[:,2]
feature_4_test = X_test_pca[:,3]
feature_5_test = X_test_pca[:,4]
feature_6_test = X_test_pca[:,5]

Y_train = y_train_resampled
Y_test = y_test

# check accuracy of predictor
accuracy_train = (accuracy_score(Y_predicted, Y_train))*100
print(f'The training accuracy is {accuracy_train}%')


score_test = w1*feature_1_test + w2*feature_2_test + w3*feature_3_test + w4*feature_4_test + w5*feature_5_test + w6*feature_6_test
Y_predicted_test = np.sign(w1*feature_1_test + w2*feature_2_test + w3*feature_3_test + w4*feature_4_test + w5*feature_5_test + w6*feature_6_test)

accuracy_test = (accuracy_score(Y_predicted_test, Y_test))*100
print(f'The testing accuracy is {accuracy_test}%')

"""Neural Network"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Use tensorflow data structure
def create_dataset(X, y):
    ds = tf.data.Dataset.from_tensor_slices((X, y))
    ds = ds.shuffle(buffer_size=len(X)) # Randomization of dataset
    return ds

# Change back since we need 0 as our low value for sigmoid output to be appropriate.
y_train_nn = y_train.replace(to_replace=-1, value=0)
y_test_nn = y_test.replace(to_replace=-1, value=0)

# Create train and test tf datasets
train_ds = create_dataset(StandardizedTrainData, y_train_nn)
test_ds = create_dataset(StandardizedTestData, y_test_nn)

train_ds = train_ds.batch(40)
test_ds = test_ds.batch(40)

epochs = 300

inputs = keras.Input(shape=30)

# Hidden layer
x = layers.Dense(16, activation="relu")(inputs)
x = layers.Dropout(0.2)(x)

y = layers.Dense(16, activation="relu")(x)
y = layers.Dropout(0.2)(y)

# Omit 20 percent of neurons before forward pass randomly in each iteration, helps avoid overfitting
# Reduces overfitting by preventing some neurons from being overactivated compared to other neurons
# Forces model to train all neurons in that layer

# Output
output = layers.Dense(1, activation="sigmoid")(y)
# Sigmoid since binary classifier

# Define model
model = keras.Model(inputs, output)

# Compile model
model.compile(loss="binary_crossentropy", optimizer="SGD", metrics=["accuracy"])

keras.utils.plot_model(model, show_shapes=True)

training_history = model.fit(train_ds, epochs=epochs, validation_data=test_ds)

# Tracking the loss of the learning process
plt.plot(training_history.history['loss'])
plt.title('Training Loss vs Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.show()

# Validating the accuracy of the learning process plotting training and val accuracy - important check
plt.plot(training_history.history['val_accuracy'])
plt.plot(training_history.history['accuracy'])
plt.title('Validation Accuracy vs Epoch')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(["Validation Accuracy", "Training Accuracy"], ncol = 1 , loc = "lower right")
plt.show()

"""**NN Decayed Learning Rate**"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import LearningRateScheduler

current_learning_rate = 0.1

def decay_learning_rate(epoch):
    global current_learning_rate
    if epoch % 10 == 0 and epoch != 0:
      current_learning_rate = current_learning_rate / 2
    return current_learning_rate

scheduler = LearningRateScheduler(decay_learning_rate)

# Use tensorflow data structure
def create_dataset(X, y):
    ds = tf.data.Dataset.from_tensor_slices((X, y))
    ds = ds.shuffle(buffer_size=len(X)) # Randomization of dataset
    return ds

# Change back since we need 0 as our low value for sigmoid output to be appropriate.
y_train_nn = y_train.replace(to_replace=-1, value=0)
y_test_nn = y_test.replace(to_replace=-1, value=0)

# Create train and test tf datasets
train_ds = create_dataset(StandardizedTrainData, y_train_nn)
test_ds = create_dataset(StandardizedTestData, y_test_nn)

train_ds = train_ds.batch(40)
test_ds = test_ds.batch(40)

epochs = 100

inputs = keras.Input(shape=30)

# Hidden layer
x = layers.Dense(16, activation="relu")(inputs)
x = layers.Dropout(0.2)(x)

y = layers.Dense(16, activation="relu")(x)
y = layers.Dropout(0.2)(y)
# Omit 20 percent of neurons before forward pass randomly in each iteration, helps avoid overfitting
# Reduces overfitting by preventing some neurons from being overactivated compared to other neurons
# Forces model to train all neurons in that layer

# Output
output = layers.Dense(1, activation="sigmoid")(y)
# Sigmoid since binary classifier

# Define model
model = keras.Model(inputs, output)

# Compile model
model.compile(loss="binary_crossentropy", optimizer="SGD", metrics=["accuracy"])

keras.utils.plot_model(model, show_shapes=True)

training_history = model.fit(train_ds, epochs=epochs, validation_data=test_ds, callbacks=[scheduler])

# Tracking the loss of the learning process
plt.plot(training_history.history['loss'])
plt.title('Training Loss vs Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.show()

# Validating the accuracy of the learning process plotting training and val accuracy - important check
plt.plot(training_history.history['val_accuracy'])
plt.plot(training_history.history['accuracy'])
plt.title('Validation Accuracy vs Epoch')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(["Validation Accuracy", "Training Accuracy"], ncol = 1 , loc = "lower right")
plt.show()

"""**Decision Trees on Dataset**"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
import graphviz
from sklearn.metrics import log_loss

df = pd.read_csv('breastcancerdata.csv')

# Split target from data and assign malignant to 1 and benign to -1 for classification
Target = df['diagnosis']
df.drop(axis=1, columns=['diagnosis'], inplace=True)

# Select a very small portion of the training data
X_train_small = X_train[:10]
y_train_small = y_train[:10]

# Creating the Decision Tree Classifier
clf = DecisionTreeClassifier(criterion='entropy') # using entropy as ID3 algorithm

# Fit the decision tree to the small training dataset
clf.fit(X_train_small, y_train_small)

# Get the predicted class probabilities for the training data
y_train_prob = clf.predict_proba(X_train_small)

# Calculate the cross-entropy loss
train_loss = log_loss(y_train_small, y_train_prob)
print("Small portion of training data loss = ",train_loss)

# Calculate cross-validation accuracy for 10 fold CV
scores = cross_val_score(clf, StandardizedTrainData, y_train, cv=15)

print("Scores = ", scores)
print("%0.2f accuracy with a standard deviation of %0.2f" % (scores.mean(), scores.std()))

clf.fit(StandardizedTrainData,y_train)

# Predict Accuracy Score
y_predicted = clf.predict(StandardizedTestData)
print("Train data accuracy:",accuracy_score(y_true = y_train, y_pred=clf.predict(StandardizedTrainData)))
print("Test data accuracy:",accuracy_score(y_true = y_test, y_pred=y_predicted))

dot_data = tree.export_graphviz(clf, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("data")

dot_data = tree.export_graphviz(clf, out_file=None,
                     class_names=np.unique(Target),
                     filled=True, rounded=True,
                     special_characters=True)
graph = graphviz.Source(dot_data)
graph

"""Boosted Decision Tree"""

# Importing the model
from sklearn.ensemble import GradientBoostingClassifier

for i in range(1, 21):
    boosted = GradientBoostingClassifier(n_estimators = i*5, learning_rate=1.0, max_depth=1, random_state=0)
    score = cross_val_score(boosted, StandardizedTrainData, y_train, scoring='accuracy', cv=10).mean()
    print("N = " + str(i*5) + " Score = " + str(round(score,2)))

# Check Test Accuracy
boosted_test = GradientBoostingClassifier(n_estimators=90, learning_rate=1.0, max_depth=1, random_state=0)

# Fit the boosted classifier on the small training set
boosted_test.fit(StandardizedTrainData, y_train)

# Get the predicted class probabilities for the training data
predicted_train = boosted_test.predict(StandardizedTrainData)
predicted = boosted_test.predict(StandardizedTestData)
print("Train Accuracy", accuracy_score(y_train, predicted_train))
print("Test Accuracy", accuracy_score(y_test, predicted))

# Select a small portion of the training data
X_train_small = StandardizedTrainData[:10]
y_train_small = y_train[:10]

# Overfitting Check

# Create a gradient boosted classifier with no regularization
boosted = GradientBoostingClassifier(n_estimators=90, max_depth=None)

# Fit the boosted classifier on the small training set
boosted.fit(X_train_small, y_train_small)

# Get the predicted class probabilities for the training data
y_train_prob = boosted.predict_proba(X_train_small)

# Calculate the cross-entropy loss
train_loss = log_loss(y_train_small, y_train_prob)
print("Small portion of training data loss = ", train_loss)

"""**Random Forest**"""

# Importing the model:
from sklearn.ensemble import RandomForestClassifier

for i in range(1, 21):
    rf = RandomForestClassifier(n_estimators = i)
    score = cross_val_score(rf, StandardizedTrainData, y_train, scoring='accuracy', cv=10).mean()
    print("N = " + str(i) + " Score = " + str(round(score,2)))

# Select a small portion of the training data
X_train_small = StandardizedTrainData[:10]
y_train_small = y_train[:10]

# Create a random forest classifier with no regularization
rf = RandomForestClassifier(n_estimators=14, max_depth=None)

# Fit the random forest on the small training set
rf.fit(X_train_small, y_train_small)

# Get the predicted class probabilities for the training data
y_train_prob = rf.predict_proba(X_train_small)

# Calculate the cross-entropy loss
train_loss = log_loss(y_train_small, y_train_prob)
print("Small portion of training data loss = ",train_loss)

# N=8 provided a good estimate for the test data
rf_final = RandomForestClassifier(n_estimators=8)

rf_final = rf_final.fit(StandardizedTrainData, y_train)

predicted_train = boosted_test.predict(StandardizedTrainData)
predicted = rf_final.predict(StandardizedTestData)

acc_test = accuracy_score(y_test, predicted)

print("Train Accuracy", accuracy_score(y_train, predicted_train))
print('The accuracy on test data is ', acc_test)