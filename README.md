# ai-breast-cancer-classification

This project was complete in a group as the final course project for SYDE 522, **Introduction to Artificial Intelligence**. 

**Group Members**: Amena Syed, Sophia Lollino, Kyle Scenna

**Data Preprocessing:**
- Data Cleaning: Removed columns such as “id” and null values to optimize data and improve training speeds
- Data Standardization: Bringing all features to a common scale for more accurate comparison
  
**Methods Utilized**
| Accuracies | Linear Classification | Linear Classification with SMOTE [1] | LDA | PCA | Neural Networks | Decision Trees |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| Training Accuracy  | 0.878  | 0.882  | 0.897  | 0.95  | 0.99  | 1.0  |
| Testing Accuracy  | 0.881 | 0.881  | 0.88  | 0.93  | 0.958  | 0.958  |

**Dataset**: https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data

**References**
[1] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, ‘SMOTE: Synthetic Minority Over-sampling Technique’, Journal of Artificial Intelligence Research, vol. 16, pp. 321–357, Jun. 2002.
