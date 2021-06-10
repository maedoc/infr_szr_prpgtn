# %% [markdown] 
# NFVI - Epileptor using custom op for Euler stepping

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.python.framework import ops
from tensorflow.python.ops import gradient_checker_v2
import sonnet as snt
import tensorflow_probability as tfp
import time
tfd = tfp.distributions
tfb = tfp.bijectors
# tfpl = tfp.layers
step_module = tf.load_op_library('./eulerstep_2d_epileptor.so')
# tf.config.set_visible_devices(tf.config.list_physical_devices('CPU'))

# %%
# tvb_syn_data = np.load("datasets/syn_data/id001_bt/syn_tvb_ez=48-79_pz=11-17-22-75.npz")
# nn = 2
# x_init_true = tf.constant(-2.0, dtype=tf.float32) * tf.ones(nn, dtype=tf.float32)
# z_init_true = tf.constant(5.0, dtype=tf.float32) * tf.ones(nn, dtype=tf.float32)
# y_init_true = tf.concat((x_init_true, z_init_true), axis=0)
# tau_true = tf.constant(25, dtype=tf.float32, shape=(1,))
# x0_true = tf.constant([-1.8, -2.5], dtype=tf.float32)
# theta_true = tf.concat((x0_true, tau_true), axis=0)
# nsteps = 300
# y = tf.TensorArray(dtype=tf.float32, size=nsteps, clear_after_read=False)
# y_next = y_init_true
# for i in tf.range(nsteps, dtype=tf.int32):
#     y_next = step_module.euler_step2d_epileptor(theta_true, y_next)
#     y = y.write(i, y_next)
# y_true = y.stack()
# # y_next = step_module.euler_step2d_epileptor(theta_true, y_init_true)
# %%
# plt.figure(figsize=(25,10));
# plt.subplot(211)
# plt.plot(y_true[:,0:nn]);
# plt.subplot(212)
# plt.plot(y_true[:,nn:2*nn]);
# plt.show()
# %% [markdown]
#### Register gradient for the Euler step custom op
# %%


@ops.RegisterGradient("EulerStep2DEpileptor")
def _euler_step2d_epileptor_grad(op, grad):
    """Gradients for Euler stepping custom op of 2D Epileptor
    
    Args:
      op: The custom op we are differentiating
      grad: Gradient of loss w.r.t. output of the custom op

    Returns:
      Gradient of loss w.r.t. inputs of custom op
    """
    dt = tf.constant(0.1, dtype=tf.float32)
    # tau = tf.constant(50.0, dtype=tf.float32)
    # TODO: make constants of Epileptor model an attribute/input of the OP for
    # better flexibility
    theta = op.inputs[0]
    current_state = op.inputs[1]
    SC = op.inputs[2]
    nn = SC.shape[0]
    x0 = theta[0:nn]
    tau = theta[nn]
    K = theta[nn+1]
    x_t_minus_1 = current_state[0:nn]
    z_t_minus_1 = current_state[nn:2*nn]
    grad_x_t = grad[0:nn]
    grad_z_t = grad[nn:2*nn]

    # gradient w.r.t x0
    grad_x0 = grad_z_t * dt * (-4.0 / tau)

    # gradient w.r.t tau
    x_diff = x_t_minus_1[tf.newaxis, :] - x_t_minus_1[:, tf.newaxis]
    diff_cplng = tf.reduce_sum(SC * x_diff, axis=1)
    dz = (1.0 / tau) * (4 * (x_t_minus_1 - x0) - z_t_minus_1 - K * diff_cplng)
    grad_tau = tf.reduce_sum(grad_z_t * dt * (-1/tau) * dz, axis=0)

    # gradient w.r.t K
    grad_K = tf.reduce_sum(grad_z_t * dt * (-1/tau) * diff_cplng)

    # gradient w.r.t x(t-1)
    SC_row_sum = tf.reduce_sum(SC, axis=1)
    SC_diag = tf.linalg.diag_part(SC)
    grad_x_t_minus_1 = grad_x_t * \
        (1 + dt * (-3.0 * x_t_minus_1**2 - 4.0 * x_t_minus_1)) + \
        grad_z_t * \
        (dt * (1/tau) * (4.0 - K * SC_diag + K * SC_row_sum)) + \
        (-K * dt / tau) * tf.linalg.matvec(SC, grad_z_t, transpose_a=True) - \
        (-K * dt / tau) * grad_z_t * SC_diag
    
    # gradient w.r.t z(t-1)
    grad_z_t_minus_1 = grad_x_t * (-dt) + grad_z_t * (1 - dt/tau)

    # concatenate the gradients to match the inputs of the op
    grad_theta = tf.concat((grad_x0,
                            tf.reshape(grad_tau, shape=(1,)),
                            tf.reshape(grad_K, shape=(1,))),
                           axis=0)
    grad_current_state = tf.concat((grad_x_t_minus_1,
                                    grad_z_t_minus_1),
                                   axis=0)
    grad_SC = None
    return [grad_theta, grad_current_state, grad_SC]
# %% [markdown]
#### Test Gradients
# %%
tvb_syn_data = np.load("datasets/syn_data/id001_bt/syn_tvb_ez=48-79_pz=11-17-22-75.npz")
SC = np.load(f'datasets/syn_data/id001_bt/network.npz')['SC']
K_true = tf.constant(np.max(SC), dtype=tf.float32, shape=(1,))
SC = SC / K_true.numpy()
SC[np.diag_indices(SC.shape[0])] = 0
SC = tf.constant(SC, dtype=tf.float32)
nn = SC.shape[0]
x_init_true = tf.constant(-2.0, dtype=tf.float32) * tf.ones(nn, dtype=tf.float32)
z_init_true = tf.constant(5.0, dtype=tf.float32) * tf.ones(nn, dtype=tf.float32)
y_init_true = tf.concat((x_init_true, z_init_true), axis=0)
tau_true = tf.constant(25, dtype=tf.float32, shape=(1,))
x0_true = tf.constant(tvb_syn_data['x0'], dtype=tf.float32)
theta_true = tf.concat((x0_true, tau_true, K_true), axis=0)
nsteps = 1
grad_thrtcl, grad_numrcl = tf.test.compute_gradient(step_module.euler_step2d_epileptor, [theta_true, y_init_true, SC], delta=1e-5)
err = np.max([np.max(np.abs(a - b)) for a, b in zip(grad_thrtcl, grad_numrcl)])
assert err < 1e-4, "Theoretical and numerical gradients did not match"
# %% [markdown]
#### Define dynamical model

# %% 
@tf.function
def integrator(nsteps, theta, y_init, SC):
    y = tf.TensorArray(dtype=tf.float32, size=nsteps, clear_after_read=False)
    y_next = y_init
    for i in tf.range(nsteps, dtype=tf.int32):
        y_next = step_module.euler_step2d_epileptor(theta, y_next, SC)
        y = y.write(i, y_next)
    return y.stack()

# %% [markdown]
#### Generate synthetic observations
# %%
tvb_syn_data = np.load("datasets/syn_data/id001_bt/syn_tvb_ez=48-79_pz=11-17-22-75.npz")
SC = np.load(f'datasets/syn_data/id001_bt/network.npz')['SC']
K_true = tf.constant(np.max(SC), dtype=tf.float32, shape=(1,))
SC = SC / K_true.numpy()
SC[np.diag_indices(SC.shape[0])] = 0
SC = tf.constant(SC, dtype=tf.float32)
nn = SC.shape[0]
x_init_true = tf.constant(-2.0, dtype=tf.float32) * tf.ones(nn, dtype=tf.float32)
z_init_true = tf.constant(5.0, dtype=tf.float32) * tf.ones(nn, dtype=tf.float32)
y_init_true = tf.concat((x_init_true, z_init_true), axis=0)
tau_true = tf.constant(25, dtype=tf.float32, shape=(1,))
x0_true = tf.constant(tvb_syn_data['x0'], dtype=tf.float32)
theta_true = tf.concat((x0_true, tau_true, K_true), axis=0)
# time_step = tf.constant(0.1, dtype=tf.float32)
nsteps = tf.constant(300, dtype=tf.int32)

# %%
start_time = time.time()
y_true = integrator(nsteps, theta_true, y_init_true, SC)
print(f"Simulation took {time.time() - start_time} seconds")
obs_data = dict()
obs_data['x'] = y_true[:, 0:nn].numpy() + tfd.Normal(loc=0, scale=0.1,
                                                     ).sample((y_true.shape[0], nn))
obs_data['z'] = y_true[:, nn:2*nn]

#%%
plt.figure(figsize=(15,7))
plt.subplot(2,1,1)
plt.plot(obs_data['x'])
plt.xlabel('Time', fontsize=15)
plt.ylabel('x', fontsize=15)

plt.subplot(2,1,2)
plt.plot(obs_data['z'])
plt.xlabel('Time', fontsize=15)
plt.ylabel('z', fontsize=15)
plt.tight_layout()
plt.show()

# plt.figure()
# plt.title("Phase space plot", fontsize=15)
# plt.plot(obs_data['x'], obs_data['z'])
# plt.xlabel('x', fontsize=15)
# plt.ylabel('z', fontsize=15)

# %% [markdown]
#### Define Generative Model

# %%  
@tf.function
def epileptor2D_log_prob(theta, x_obs, SC):
    # time_step = tf.constant(0.1)
    nsteps = tf.constant(300, dtype=tf.int32)
    eps = tf.constant(0.1)
    # y_init = tf.constant([-2.0, 5.0], dtype=tf.float32)
    nn = x_obs.shape[1]
    x0 = theta[0:nn]
    x0_trans = tf.constant(-5.0, dtype=tf.float32) + \
        tf.constant(5.0, dtype=tf.float32)*tf.math.sigmoid(x0)
    tau = theta[nn]
    tau_trans = tf.constant(10.0, dtype=tf.float32) + \
        tf.constant(90.0, dtype=tf.float32)*tf.math.sigmoid(tau)
    K = theta[nn+1]
    K_trans = 10*tf.math.sigmoid(K)
    theta_trans = tf.concat((x0_trans, \
                             tf.reshape(tau_trans, shape=(1,)), \
                             tf.reshape(K_trans, shape=(1,))), axis=0)
    y_init = theta[nn+2:3*nn+2]
    x_init = y_init[0:nn]
    z_init = y_init[nn:2*nn]
    x_init_trans = tf.constant(-5.0, dtype=tf.float32) + \
        tf.constant(3.5, dtype=tf.float32) * tf.math.sigmoid(x_init)
    z_init_trans = tf.constant(2, dtype=tf.float32) + \
        tf.constant(4, dtype=tf.float32) * tf.math.sigmoid(z_init)
    y_init_trans = tf.concat((x_init_trans, z_init_trans), axis=0)
    
    
    # tf.print('x0 =', x0, '\nx0_trans =', x0_trans, '\ntau =', tau, \
    #         '\ntau_trans =', tau_trans, '\n x_init =', x_init, \
    #         '\n x_init_trans =', x_init_trans, '\nz_init =', z_init, \
    #         '\nz_init_trans =', z_init_trans, '\nK =', K, \
    #         '\nK_trans =', K_trans, summarize=-1, output_stream="file://debug.log")
    
    # Compute Likelihood
    y_pred = integrator(nsteps, theta_trans, y_init_trans, SC)
    x_mu = y_pred[:, 0:nn]
    # tf.print("NaN in x_mu = ", tf.reduce_any(tf.math.is_nan(x_mu)))
    likelihood = tf.reduce_sum(tfd.Normal(loc=x_mu, scale=eps).log_prob(x_obs))
    
    # Compute Prior probability
    prior_x0 = tf.reduce_sum(tfd.Normal(loc=0.0, scale=5.0).log_prob(x0))
    prior_tau = tfd.Normal(loc = 0, scale = 5.0).log_prob(tau)
    # y_init_mu=tf.concat((-3.0*tf.ones(nn), 4.0*tf.ones(nn)), axis = 0)
    prior_K = tfd.Normal(loc=0.0, scale=10.0).log_prob(K)
    prior_y_init = tfd.MultivariateNormalDiag(
        loc=tf.zeros(2*nn), scale_diag=10*tf.ones(2*nn)).log_prob(y_init)
    
    return likelihood + prior_x0 + prior_tau  + prior_K + prior_y_init

# %%
# @tf.function
# def find_log_prob(theta):
#     return gm.log_prob(theta)
import time
start_time = time.time()
# theta = tf.concat((x0, ))
theta = tf.zeros(3*nn+2, dtype=tf.float32)
print(epileptor2D_log_prob(theta, obs_data['x'], SC))
print("Elapsed: %s seconds" % (time.time()-start_time))

#%%
# x0_range = np.linspace(-3.0,0.0,10)
# tau_range = np.linspace(10,30.0,10)
# gm_log_prob = np.zeros((x0_range.size, tau_range.size))
# for i, x0_val in enumerate(x0_range):
#     for j, tau_val in enumerate(tau_range):
#         gm_log_prob[j,i] = epileptor2D_log_prob([tf.constant(x0_val, dtype=tf.float32), tf.constant(np.log(tau_val), dtype=tf.float32)], obs_data['x'])

#%%
# x0_mesh, tau_mesh = np.meshgrid(x0_range, tau_range)
# tau_mesh = tau_mesh + 10.0
# plt.contour(x0_mesh, tau_mesh, gm_log_prob, levels=1000)
# plt.xlabel('x0', fontsize=15)
# plt.ylabel('tau', fontsize=15)
# plt.colorbar()
# plt.title('True unnormalized Posterior')
# # find_log_prob([-3.0, tf.math.log(20.0)])

# %% [markdown]
#### Define the variational posterior using Masked Autoregressive Flows (MAF)

#%% 
num_bijectors = 5
tf.random.set_seed(1234567)
# permutation = tf.random.shuffle(tf.range(3*nn+2))

bijectors = []
for i in range(num_bijectors-1):
    made = tfb.AutoregressiveNetwork(
        params=2, hidden_units=[2048, 2048], activation='tanh')
    maf = tfb.MaskedAutoregressiveFlow(shift_and_log_scale_fn=made)
    bijectors.append(maf)
    bijectors.append(tfb.Permute(
        permutation=tf.random.shuffle(tf.range(3*nn+2))))
    bijectors.append(tfb.BatchNormalization())

made = tfb.AutoregressiveNetwork(
    params=2, hidden_units=[2048, 2048], activation='tanh')
maf = tfb.MaskedAutoregressiveFlow(shift_and_log_scale_fn=made)
bijectors.append(maf)
bijectors.append(tfb.BatchNormalization())
chained_maf = tfb.Chain(list(reversed(bijectors)))
base_dist = tfd.Independent(
    tfd.Normal(loc=tf.zeros(3*nn+2, dtype=tf.float32),
               scale=0.1 * tf.ones(3*nn+2, dtype=tf.float32),
               name='Base Distribution'),
               reinterpreted_batch_ndims=1)
flow_dist = tfd.TransformedDistribution(distribution=base_dist,
                                        bijector=chained_maf,
                                        name='Variational Posterior')

#%%
# flow_log_prob = np.zeros((x0_range.size, tau_range.size))
# for i, x0_val in enumerate(x0_range):
#     for j, tau_val in enumerate(tau_range):
#         flow_log_prob[j,i] = flow_dist.log_prob([x0_val, tau_val])

#%%
# plt.contour(x0_mesh, tau_mesh, flow_log_prob, levels=1000)
# plt.colorbar()
# plt.title('Variational Posterior before training')

# %% [markdown]
#### Define functions to compute loss and gradients

#%%
@tf.function
def loss(posterior_approx, base_dist_samples, x_obs, SC):
    posterior_samples = posterior_approx.bijector.forward(base_dist_samples)
    # tf.print(posterior_samples)
    # tf.print(posterior_samples)
    nsamples = base_dist_samples.shape[0]
    loss_val = tf.reduce_sum(posterior_approx.log_prob(posterior_samples)/nsamples)
    for theta in posterior_samples:
        # tf.print("theta: ", theta, summarize=-1)
        gm_log_prob = epileptor2D_log_prob(theta, x_obs, SC)
        # posterior_approx_log_prob = posterior_approx.log_prob(theta)
        loss_val -= gm_log_prob/nsamples
        # tf.print("gm_log_prob:",gm_log_prob, "\nposterior_approx_log_prob:", posterior_approx_log_prob)
        # tf.print("loss_val: ", loss_val)
    return loss_val

# y_init = tf.constant([-2.0, 5.0])
# dt = tf.constant(0.1)
# solution_times = dt * np.arange(0, 300)
# eps = tf.constant(0.1)

@tf.function
def get_loss_and_gradients(posterior_approx, base_dist_samples, x_obs, SC):
    # nsamples = base_dist_samples.shape[0]
    with tf.GradientTape() as tape:
        loss_val = loss(posterior_approx, base_dist_samples, x_obs, SC)
        return loss_val, tape.gradient(loss_val, posterior_approx.trainable_variables)

# %%
initial_learning_rate = 1e-3
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate,
    decay_steps=10,
    decay_rate=0.96,
    staircase=True)

optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
# %%
# # @tf.function
# # def find_loss():
# #     loss_val = loss(flow_dist, tf.constant([[-0.29448965, -0.95975673],[ 0.17711619,  0.222046]], dtype=tf.float32))
# #     return loss_val
# base_dist_samples = base_dist.sample((5))
# for i in range(10):
#     loss_val, grads = get_loss_and_gradients(flow_dist, base_dist_samples)
#     tf.print("gradient norm = ", tf.norm(grads))
#     tf.print('Final loss_val = ', loss_val)
#     # tf.print(grads)
#     optimizer.apply_gradients(zip(grads, flow_dist.trainable_variables))

# %%
# base_dist_samples = tf.constant([[-0.29448965, -0.95975673],[ 0.17711619,  0.222046]], dtype=tf.float32)
# posterior_samples = flow_dist.bijector.forward(base_dist_samples)
# for theta in posterior_samples:
#     gm_log_prob = gm.log_prob(theta)
#     print(gm_log_prob)


# %% [markdown]
#### Training
# %%
batch_size = 10
base_dist_samples = tf.data.Dataset.from_tensor_slices(
    base_dist.sample((1000))).batch(batch_size)

# %%
num_epochs = 5

training_loss = []
start_time = time.time()

for epoch in range(num_epochs):
    for batch_base_dist_samples in base_dist_samples.as_numpy_iterator():
        loss_value, grads = get_loss_and_gradients(flow_dist, tf.constant(
            batch_base_dist_samples, dtype=tf.float32), obs_data['x'], SC)
        grads = [tf.divide(el, batch_size) for el in grads]
        grads = [tf.clip_by_norm(el, 1000) for el in grads]
        # tf.print("gradient norm = ", [tf.norm(el) for el in grads], \
                # output_stream="file://debug.log")
        tf.print("loss: ", loss_value)
        training_loss.append(loss_value)
        optimizer.apply_gradients(
            zip(grads, flow_dist.trainable_variables))
    # if ((epoch+1) % 10 == 0):
    #     print(f'Epoch {epoch + 1}:\n Training Loss: {loss_value}')
    print(f"Elapsed {time.time()-start_time} seconds for {epoch+1} Epochs")

# %% [markdown]
#### Results

# %%
samples = flow_dist.sample((100))
# samples = np.zeros([1000, 494], dtype=np.float)
# i = 0
# for batch_base_dist_samples in base_dist_samples.as_numpy_iterator():
#     samples[i*batch_size:(i+1)*batch_size] = flow_dist.bijector.forward(batch_base_dist_samples)
#     i += 1
# samples = tf.constant(samples, dtype=tf.float32)
# samples_mean = tf.reduce_mean(samples, axis=0)
# %%

plt.figure(figsize=(25,5))
plt.subplot(1,4,1)
plt.hist(samples[:,0], density=True, color='black')
plt.axvline(x0_true, color='red', label='Ground truth')
plt.legend()
plt.xlabel('x0')

plt.subplot(1,4,2)
plt.hist(10 + np.exp(samples[:,1]), density=True, color='black')
plt.axvline(tau_true, color='red', label='Ground truth')
plt.legend()
plt.xlabel('tau')

plt.subplot(1,4,3)
plt.hist(samples[:,2], density=True, color='black')
plt.axvline(x_init_true, color='red', label='Ground truth')
plt.legend()

plt.xlabel('x_init')
plt.subplot(1,4,4)
plt.hist(samples[:,3], density=True, color='black')
plt.axvline(z_init_true, color='red', label='Ground truth')
plt.legend()
plt.xlabel('z_init')

# %%
x0 = samples[:, 0:nn]
x0_trans = tf.constant(-5.0, dtype=tf.float32) + tf.constant(5.0, dtype=tf.float32)*tf.math.sigmoid(x0)
tau = samples[:, nn]
tau_trans = tf.constant(10.0, dtype=tf.float32) + tf.constant(90.0, dtype=tf.float32)*tf.math.sigmoid(tau)
y_init = samples[:, nn+1:3*nn+1]
x_init = y_init[:, 0:nn]
z_init = y_init[:, nn:2*nn]
x_init_trans = tf.constant(-5.0, dtype=tf.float32) + tf.constant(3.5, dtype=tf.float32) * tf.math.sigmoid(x_init)
z_init_trans = tf.constant(2, dtype=tf.float32) + tf.constant(4, dtype=tf.float32) * tf.math.sigmoid(z_init)
y_init_trans = tf.concat((x_init_trans, z_init_trans), axis=1)
K = samples[:, 3*nn+1]
K_trans = 10*tf.math.sigmoid(K)


# %%
x_pred = np.zeros((10, nsteps, nn))
z_pred = np.zeros((10, nsteps, nn))
t_init = tf.constant(0.0, dtype=tf.float32)
time_step = tf.constant(0.1, dtype=tf.float32)
nsteps = 300
for i in range(10):
    theta_trans_i = tf.concat((x0_trans[i], \
                             tf.reshape(tau_trans[i], shape=(1,)), \
                             tf.reshape(K_trans[i], shape=(1,))), axis=0)
    y_pred = integrator(nsteps, theta_trans_i, y_init_trans[i], SC)
    x_pred[i]=y_pred.numpy()[:, 0:nn]
    z_pred[i]=y_pred.numpy()[:, nn:2*nn]
# %%
plt.figure(figsize=(15,5))
plt.violinplot(x0_trans.numpy());
plt.scatter(np.arange(0, x0_true.shape[0]), x0_true, color='red', marker='.', s=20)
plt.xlabel(r'$x_0$', fontsize=20)
plt.figure(figsize=(10,5))
plt.violinplot(tau_trans.numpy());
plt.xlabel(r'$\tau$', fontsize=20)
plt.plot(1,tau_true, color='red', marker='.', markersize=20);
plt.figure(figsize=(10,5))
plt.violinplot(K_trans.numpy());
plt.plot(1,K_true, color='red', marker='.', markersize=20);
plt.xlabel('K', fontsize=20);

# %%
plt.figure(figsize=(15,7))
plt.subplot(2,1,1)
plt.plot(x_pred.mean(axis=0), label='Prediction at Posterior Mean', lw=1.0, color='black')
plt.plot(obs_data['x'], color='red', label='Ground truth', alpha=0.8)
plt.xlabel('Time', fontsize=20)
plt.ylabel('x', fontsize=20)
# plt.legend()

plt.subplot(2,1,2)
plt.plot(z_pred.mean(axis=0), label='Prediction at Posterior Mean', lw=1.0, color='black')
plt.plot(obs_data['z'], color='red', label='Ground truth', alpha=0.8)
plt.xlabel('Time', fontsize=20)
plt.ylabel('z', fontsize=20)
plt.tight_layout()
# plt.legend()

# plt.figure()
# plt.title("Phase space plot", fontsize=15)
# plt.plot(y[:,0], y[:,1], color='black', lw=5.0)
# plt.plot(obs_data['x'], obs_data['z'], color='red', alpha=0.8)
# plt.xlabel('x', fontsize=15)
# plt.ylabel('z', fontsize=15)

# %%
for i, theta in enumerate(samples):
    print(f"sample {i} ", flow_dist.log_prob(theta) - epileptor2D_log_prob(theta, obs_data['x'], SC))

# %%

def logit(x):
    return tf.math.log(x) - tf.math.log(1.0 - x)
theta = np.zeros(3*nn+2)
theta[0:nn] = logit((x0_true + 5.0)/ 5.0)
theta[nn] = logit((tau_true - 10.0)/90.0)
theta[nn+1:2*nn+1] = logit((x_init_true + 10.0)/9.0)
theta[2*nn+1:3*nn+1] = logit((z_init_true - 2.0)/8.0)
theta[3*nn+1] = logit((K_true)/10.0)

theta = tf.constant(theta, dtype=tf.float32)
# %%
flow_dist.log_prob(theta) - epileptor2D_log_prob(theta, obs_data['x'], SC)