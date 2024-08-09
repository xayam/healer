from kan import *

# create a KAN: 2D inputs, 1D output, and 5 hidden neurons.
# cubic spline (k=3), 5 grid intervals (grid=5).

model = KAN(width=[64, 5, 5, 5, 64], grid=5, k=3, seed=0)
# model.train()
