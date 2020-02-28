import tensorflow as tf
import numpy as np

X_train = np.array(np.random.randn(50,1)) # One dimension -> 50 instances
Y_train = X_train*X_train + 2*X_train + 3

# X_train = [x for x in range(1,11)]
# Y_train = [x for x in range(3,22,2)]

X = tf.placeholder(tf.float32)
Y = tf.placeholder(tf.float32)

epochs = 5000
size_input = 1
size_hidden1 = 3
size_hidden2 = 6
size_output = 1

# Define Parameters to be learnt
Wh1 = tf.Variable(tf.random_normal([size_input, size_hidden1]))
bh1 = tf.Variable(tf.random_normal([1, size_hidden1]))

Wh2 = tf.Variable(tf.random_normal([size_hidden1, size_hidden2]))
bh2 = tf.Variable(tf.random_normal([1, size_hidden2]))

Wo = tf.Variable(tf.random_normal([size_hidden2, size_output]))
bo = tf.Variable(tf.random_normal([1, size_output]))


# Predicted output
net_h1 = tf.matmul(X,Wh1) + bh1
act_h1 = tf.nn.relu(net_h1)

net_h2 = tf.matmul(act_h1,Wh2) + bh2
act_h2 = tf.nn.relu(net_h2)

net_op = tf.matmul(act_h2,Wo) + bo
act_op = tf.nn.relu(net_op) # Not necessary

pred = act_op

# Loss function - MSE
# Reduce_mean reduces dimension of tensor
# formula = (1/2) * ((Summation(Ytrain - Ypred)) ^ 2)
loss = tf.reduce_mean(tf.pow(Y - pred, 2.0))/2.0

init = tf.global_variables_initializer()
opt = tf.train.GradientDescentOptimizer(learning_rate = 0.002).minimize(loss)

epochs = 10000
with tf.Session() as sess:
    sess.run(init)

    for i in range(epochs):
        sess.run(opt, feed_dict={X:X_train,Y:Y_train})

        # tfprint("Epoch: ", i, "Loss: ", loss.eval(feed_dict={Y:Y_train,X:X_train}))
        
    # X_test = np.asarray([[1.1],[1.2],[1.3],[0.9],[0.8]])
    X_test = np.asarray([[1],[2],[3],[4],[5]])
    print(np.shape(X_test))
    print(sess.run(pred, feed_dict={X:X_test}))