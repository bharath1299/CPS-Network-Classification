from sklearn.ensemble import RandomForestClassifier
from .resource_logger import log_resource_utilization
import time

class AppScanner(object):

    def __init__(self, threshold=0.9):
        """AppScanner object for recognising applications in network traffic.
            This implementation uses a Single Large Random Forest.

            Parameters
            ----------
            threshold : float, default=0.9
                Threshold for certainty required to make a prediction.
            """
        # Set threshold
        self.threshold = threshold
        # Create classifier
        self.classifier = RandomForestClassifier(criterion='gini',
                                                 max_features='sqrt',
                                                 n_estimators=150)

    def fit(self, X, y):
        """Fit model with given training data and labels.

            Parameters
            ----------
            X : np.array of shape=(n_samples, n_features)
                Data to fit the model with.

            y : np.array of shape=(n_samples,)
                Labels corresponding to samples in X.

            Returns
            -------
            self : self
                Returns self for fit_predict method.
            """
        start_time = time.time()
        # Fit classifier with given data.
        self.classifier.fit(X, y)

        #After ML Training
        log_resource_utilization("After Training ML Model", data_processed=len(X), start_time=start_time)
        
        # Return self for fit_predict method
        return self

    def predict(self, X):
        """Predict the class of X from the trained model.

            Parameters
            ----------
            X : np.array of shape=(n_samples, n_features)
                Data to predict.

            Returns
            -------
            result : np.array of shape=(n_samples,)
                Prediction of labels for data X.
                Labels are -1 if they cannot be predicted.
            """
        start_time = time.time()
        # Get maximum prediction probabilities
        probabilities = self.classifier.predict_proba(X).max(axis=1)
        # Get prediction
        prediction = self.classifier.predict(X)

        #After fingerprint matching
        log_resource_utilization("After Fingerprint Matching", data_processed=len(X), start_time=start_time)
        
        # Set uncertain predictions to -1
        prediction[probabilities < self.threshold] = -1

        #After classification validation
        log_resource_utilization("After Classification Validation", data_processed=len(X), start_time=start_time)

        # Return predictions
        return prediction

    def fit_predict(self, X, y):
        """Fit model and return the prediction on the same data.

            Parameters
            ----------
            X : np.array of shape=(n_samples, n_features)
                Data to fit the model with and to predict.

            y : np.array of shape=(n_samples,)
                Labels corresponding to samples in X.

            Returns
            -------
            result : np.array of shape=(n_samples,)
                Prediction of labels for data X.
                Labels are -1 if they cannot be predicted.
            """
        return self.fit(X, y).predict(X)
