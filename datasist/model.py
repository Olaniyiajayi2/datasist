'''
This module contains all functions relating to modeling in using sklearn library.

'''

from sklearn.metrics import roc_curve,confusion_matrix, precision_score,accuracy_score, recall_score,f1_score, make_scorer
from sklearn.model_selection import KFold, cross_val_score
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from .visualizations import plot_auc


def train_classifier(X_train = None, y_train=None, X_val=None, y_val=None, estimator=None, cross_validate=False, cv=5, show_roc_plot=True, save_plot=False):
    '''
    Train a classification estimator and calculate numerous performance metric.

    Parameters:
    ----------------------------
        X_train: Array, DataFrame, Series.

            The feature set (x) to use in training an estimator in other predict the outcome (y).

        y_train: Series, 1-d array, list

            The ground truth value for the train dataset

        X_val: Array, DataFrame. Series.

            The feature set (x) to use in validating a trained estimator.

        y_val: Series, 1-d array, list

            The ground truth value for the validation dataset.

        estimator: sklearn estimator.

            Sklearn estimator that implements the fit and predict functions.

        cross_validate: Bool, default False

            Use a cross validation strategy or not.
        
        cv: Int, default 5

            Number of folds to use in cross validation.
        
        show_roc_curve: Bool, default True.

            Plot a ROC plot showing estimator performance.
        
        save_plot: Bool, default False.
            Save the plot as a png file.
    
'''
    if X_train is None:
        raise ValueError("X_train: Expecting a DataFrame/ numpy2d array, got 'None'")
    
    if y_train is None:
        raise ValueError("y_train: Expecting a Series/ numpy1D array, got 'None'")

    #initialize variables to hold calculations
    pred, acc, f1, precision, recall, confusion_mat = 0, 0, 0, 0, 0, None

    if cross_validate:
        dict_scorers  = {'acc' : accuracy_score,
                        'f1' : f1_score,
                        'precision': precision_score, 
                        'recall' : recall_score
                        }


        metric_names = ['Accuracy', 'F1_score', 'Precision', 'Recall']

        for metric_name, scorer in zip(metric_names, dict_scorers):
            cv_score = np.mean(cross_val_score(estimator, X_train, y_train, scoring=make_scorer(dict_scorers[scorer]),cv=cv))
            print("{} is {}".format(metric_name,  round(cv_score * 100, 4)))

        #TODO Add cross validation function for confusion matrix
  
    else:
        if X_val is None:
            raise ValueError("X_val: Expecting a DataFrame/ numpy array, got 'None'")
        
        if y_val is None:
            raise ValueError("y_val: Expecting a Series/ numpy1D array, got 'None'")

        estimator.fit(X_train, y_train)
        pred = estimator.predict(X_val)
        get_classification_report(y_val, pred, show_roc_plot, save_plot)



def plot_feature_importance(estimator=None, col_names=None):
    '''
    Plots the feature importance from a trained scikit learn estimator
    as a bar chart.

    Parameters:
    -----------
        estimator: scikit  learn estimator.

            Model that has been fit and contains the feature_importance_ attribute.

        col_names: list

            The names of the columns. Must map unto feature importance array.

    Returns:
    --------
        Matplotlib figure showing feature importances
    '''
    if estimator is None:
        raise ValueError("estimator: Expecting an estimator that implements the fit api, got None")
    if col_names is None:
        raise ValueError("col_names: Expecting a list of column names, got 'None'")
    
    if len(col_names) != len(estimator.feature_importances_):
        raise ValueError("col_names: Lenght of col_names must match lenght of feature importances")

    imps = estimator.feature_importances_
    feats_imp = pd.DataFrame({"features": col_names, "importance": imps}).sort_values(by='importance', ascending=False)
    sns.barplot(x='features', y='importance', data=feats_imp)
    plt.xticks(rotation=90)
    plt.title("Feature importance plot")
    plt.show()


def make_submission_csv(estimator=None, X_train=None, y_train=None, test_data=None,
                  sample_submision_file=None, sub_col_name=None, name="final_submission"):
    '''
    Train a estimator and makes prediction with it on the final test set. Also
    returns a sample submission file for data science competitions
    
    Parameters:
    -----------------------
    estimator: Sklearn estimator.

        An sklearn estimator that implements the fit and predict functions.

    X_train: Array, DataFrame, Series.

        The feature set (x) to use in training an estimator to predict the outcome (y).

    y_train: Series, 1-d array, list

        The ground truth value for the train dataset

    test_data: Array, DataFrame. Series.

        The final test set (x) to predict on.
    
    sample_submision_file: DataFrame, Series.

        A sample csv file provided by data science competition hosts to use in creating your final submission.

    sub_col_name: String.

        Name of the prediction column in the sample submission file.

    name: String.

        Name of the created submission file.

    Return:

        Csv file saved in current working directory
    '''
    estimator.fit(X_train, y_train)
    pred = estimator.predict(test_data)

    sub = sample_submision_file
    sub[sub_col_name] = pred
    sub.to_csv(name + '.csv', index=False)
    print("File has been saved to current working directory")



def get_classification_report(y_true=None, y_pred=None, show_roc_plot=True, save_plot=False):
    '''
    Generates performance report for a classification problem.

    Parameters:
    ------------------
    y_true: Array, series, list.

        The truth/ground value from the train data set.
    
    y_pred: Array, series, list.

        The predicted value by a trained model.

    show_roc_plot: Bool, default True.

        Show the model ROC curve.

    save_plot: Bool, default True.

        Save the plot to the current working directory.

    '''
    acc = accuracy_score(y_train, pred)
    f1 = f1_score(y_train, pred)
    precision = precision_score(y_train, pred)
    recall = recall_score(y_train, pred)
    confusion_mat = confusion_matrix(y_train, pred)

    print("Accuracy is ", round(acc * 100))
    print("F1 score is ", round(f1 * 100))
    print("Precision is ", round(precision * 100))
    print("Recall is ", round(recall * 100))
    print("*" * 100)
    print("confusion Matrix")
    print('                 Score positive    Score negative')
    print('Actual positive    %6d' % confusion_mat[0,0] + '             %5d' % confusion_mat[0,1])
    print('Actual negative    %6d' % confusion_mat[1,0] + '             %5d' % confusion_mat[1,1])
    print('')

    if show_roc_plot:        
        plot_auc(y_train, pred)

        if save_plot:
            plt.savefig("roc_plot.png")
