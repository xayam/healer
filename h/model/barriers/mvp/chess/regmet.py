from sklearn.metrics import \
    mean_squared_error, mean_absolute_error, r2_score, \
    explained_variance_score, mean_pinball_loss, \
    d2_pinball_score, d2_absolute_error_score


class RegressionMetrics:

    def __init__(self, y_true, y_pred, multi_output='uniform_average'):
        self.y_true = y_true
        self.y_pred = y_pred
        self.multi_output = multi_output
        self.metrics = [
            mean_squared_error, mean_absolute_error, r2_score,
            explained_variance_score, mean_pinball_loss,
            d2_pinball_score, d2_absolute_error_score
        ]
        self.vision()

    def vision(self):
        for metric in self.metrics:
            print(
                f"{metric.__name__.rjust(25, ' ')} | " +
                f"{metric()}"
            )

    def mean_squared_error(self):
        return mean_squared_error(
            self.y_true, self.y_pred, self.multi_output
        )

    def mean_absolute_error(self):
        return mean_absolute_error(
            self.y_true, self.y_pred, self.multi_output
        )

    def r2_score(self):
        return r2_score(
            self.y_true, self.y_pred, self.multi_output
        )

    def explained_variance_score(self):
        return explained_variance_score(
            self.y_true, self.y_pred, self.multi_output
        )

    def mean_pinball_loss(self):
        return mean_pinball_loss(
            self.y_true, self.y_pred, self.multi_output
        )

    def d2_pinball_score(self):
        return d2_pinball_score(
            self.y_true, self.y_pred, self.multi_output
        )

    def d2_absolute_error_score(self):
        return d2_absolute_error_score(
            self.y_true, self.y_pred, self.multi_output
        )


