import random
import numpy as np
import sklearn as sk
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import KFold, cross_val_score
INPUT_SIZE = 200

hyperparams = {
	'hidden_layer_sizes' : [(5, 2), (5, 5), (10,), (2, 5)],
	'alphas': [1e-5, 0.001, .01, 10.0]
}

def main():
	# read in csv text, modify training data and labels
	training = pd.read_csv('reviews_tr.csv')
	training_text = training['text'][0:INPUT_SIZE]
	training_labels = training['label'][0:INPUT_SIZE].values.reshape((INPUT_SIZE, 1))
	zeros = np.where(training_labels == 0)
	training_labels[zeros] = -1
	del training, zeros

	# read in csv, modify test 
	test = pd.read_csv('reviews_te.csv')
	test_text = test['text'][0:INPUT_SIZE]
	test_labels = test['label'][0:INPUT_SIZE].values.reshape((INPUT_SIZE, 1))
	zeros = np.where(test_labels == 0)
	test_labels[zeros] = -1
	del test, zeros

	unigram_train, unigram_test = build_unigram(training_text, test_text)

	best_alpha, best_dims = select_hyperparams(unigram_train, training_labels, hyperparams['alphas'], hyperparams['hidden_layer_sizes'])
	print("selected hyperparamters: alpha=%f dims=%s" % (best_alpha, str(best_dims)))

	classifier = MLPClassifier(solver='lbgfs', alpha=best_alpha, hidden_layer_sizes=best_dims, random_state=1)
	classifier.fit(unigram_train, training_labels)

	print("Final training set score: %f" % classifier.score(unigram_train, training_labels))
	print("Final test set score: %f" % classifier.score(unigram_test, test_labels))


# takes in raw data
def build_unigram(training_data, test_data):
	vectorizer = CountVectorizer()
	unigram_tr = vectorizer.fit_transform(training_data)
	unigram_te = vectorizer.transform(test_data)
	print "built unigram feature representation"
	return unigram_tr, unigram_te

def select_hyperparams(X, Y, alphas, dims):
	best_tr_accuracy_so_far = 0.0
	best_hyperparams = (alphas[0], dims[0])
	for a in alphas:
		for dim in dims:
			print("Evaluating classifier with alpha=%f and dims=%s" % (a, str(dim)))
			nnet = construct_classifier_with_hyperparameters(a, dim)
			k = 5
			avg_accuracy = Kfold_cross_validation(k, X, Y, nnet)
			if avg_accuracy > best_tr_accuracy_so_far:
				best_hyperparams = (a, dim)

	return best_hyperparams


def Kfold_cross_validation(k, X, Y, classifier):
	k_folds = KFold(n_splits = k)
	n = 0
	errorSum = 0.0
	for train, test in k_folds.split(X):
		n += 1
		classifier.fit(X[train], Y[train])
		err = classifier.score(X[test], Y[test])
		print("Training set score on trial %d: %f" % (n, err))
		errorSum += err

	avg_error = float(errorSum) / float(k)
	return avg_error

def construct_classifier_with_hyperparameters(alpha_val, nnet_dims):
	return MLPClassifier(solver='lbgfs', alpha=alpha_val, hidden_layer_sizes=nnet_dims, random_state=1)

if __name__ == "__main__":
	main()
