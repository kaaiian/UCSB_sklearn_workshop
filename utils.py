import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.model_selection import cross_validate, cross_val_score, cross_val_predict, learning_curve, GridSearchCV

class MidpointNormalize(Normalize):

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

def plot_grid_search(grid):
    parameters = [x[6:] for x in list(grid.cv_results_.keys()) if 'param_' in x]

    param1 = list(set(grid.cv_results_['param_'+parameters[0]]))
    param2 =list(set(grid.cv_results_['param_'+parameters[1]]))
    scores = grid.cv_results_['mean_test_score'].reshape(len(param1),
                                                         len(param2))

    plt.figure(figsize=(8, 6))
    plt.subplots_adjust(left=.2, right=0.95, bottom=0.15, top=0.95)
    plt.imshow(scores, interpolation='nearest', cmap=plt.cm.hot,
               norm=MidpointNormalize(vmin=0.2, midpoint=0.62))
    plt.xlabel(parameters[0])
    plt.ylabel(parameters[1])
    plt.colorbar()
    plt.xticks(np.arange(len(param1)), param1, rotation=45)
    plt.yticks(np.arange(len(param2)), param2)
    plt.title('grid search')
    plt.show()

def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=None, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and training learning curve.
    inspired by:
        https://scikit-learn.org/stable/auto_examples/model_selection/plot_learning_curve
                      .html#sphx-glr-auto-examples-model-selection-plot-learning-curve-py

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross-validation,
          - integer, to specify the number of folds.
          - :term:`CV splitter`,
          - An iterable yielding (train, test) splits as arrays of indices.

        For integer/None inputs, if ``y`` is binary or multiclass,
        :class:`StratifiedKFold` used. If the estimator is not a classifier
        or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validators that can be used here.

    n_jobs : int or None, optional (default=None)
        Number of jobs to run in parallel.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    train_sizes : array-like, shape (n_ticks,), dtype float or int
        Relative or absolute numbers of training examples that will be used to
        generate the learning curve. If the dtype is float, it is regarded as a
        fraction of the maximum size of the training set (that is determined
        by the selected validation method), i.e. it has to be within (0, 1].
        Otherwise it is interpreted as absolute sizes of the training sets.
        Note that for classification the number of samples usually have to
        be big enough to contain at least one sample from each class.
        (default: np.linspace(0.1, 1.0, 5))
    """
    plt.figure(figsize=(7,7))
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    plt.tick_params(direction='in', length=5, bottom=True, top=True, left=True, right=True)
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    plt.show()

def rf_feature_importance(rf, X_train, N='all', std_deviation=False):
    '''Get feature importances for trained random forest object
    
    Parameters
    ----------
    rf : sklearn RandomForest object
    	This needs to be a sklearn.ensemble.RandomForestRegressor of RandomForestClassifier object that has been fit to data
    N : integer, optional (default=10)
    	The N most important features are displayed with their relative importance scores
    std_deviation : Boolean, optional (default=False)
    	Whether or not error bars are plotted with the feature importance. (error can be very large if maximum_features!='all' while training random forest
    Output
    --------
    graphic :
    	return plot showing relative feature importance and confidence intervals
    Examples
    --------
    >>> from sklearn.ensemble import RandomForestRegressor
    >>> rf = RandomForestRegressor(max_depth=20, random_state=0)
    >>> rf.fit(X_train, y_train)
    >>> rf_feature_importance(rf, N=15)
    ''' 
    if N=='all':
    	N=X_train.shape[1]
    importance_dic = {}
    importances = rf.feature_importances_
    std = np.std([tree.feature_importances_ for tree in rf.estimators_],
    			 axis=0)
    indices = np.argsort(importances)[::-1]
    indices = indices[0:N]
    
    # Print the feature ranking
    print("Feature ranking:")
    
    for f in range(0, N):
    	importance_dic[X_train.columns.values[indices[f]]]=importances[indices[f]]
    	print(("%d. feature %d (%.3f)" % (f + 1, indices[f], importances[indices[f]])),':', X_train.columns.values[indices[f]])
    
    
    # Plot the feature importances of the forest
    plt.figure(figsize=(6,6))
    plt.title("Feature importances")
    if std_deviation == True:
    	plt.bar(range(0, N), importances[indices], color="r", yerr=std[indices], align="center")
    else:
    	plt.bar(range(0, N), importances[indices], color="r", align="center")
    plt.tick_params(direction='in', length=5, bottom=True, top=True, left=True, right=True)
    plt.xticks(range(0, N), indices, rotation=90)
    plt.xlim([-1, N])
    plt.show()
    return X_train.columns.values[indices]