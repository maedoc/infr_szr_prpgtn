functions {

  matrix vector_differencing(row_vector x) {
    matrix[num_elements(x), num_elements(x)] D;
    for (i in 1:num_elements(x)) {
      D[i] = x - x[i];
    }
    return D;
  }

  row_vector x_step(row_vector x, row_vector z, real I1, real time_step) {
    int nn = num_elements(x);
    row_vector[nn] x_next;
    row_vector[nn] I1_vec = rep_row_vector(I1 + 1.0, nn);
    row_vector[nn] dx = I1_vec - (x .* x .* x) - 2.0 * (x .* x) - z;
    x_next = x + (time_step * dx);
    return x_next;
  }

  row_vector z_step(row_vector x, row_vector z, row_vector x0, matrix FC,
		    real time_step, real tau0) {
    int nn = num_elements(z);
    row_vector[nn] z_next;
    matrix[nn, nn] D = vector_differencing(x);
    row_vector[nn] gx = to_row_vector(rows_dot_product(FC, D));
    row_vector[nn] dz = inv(tau0) * (4 * (x - x0) - z - gx);
    z_next = z + (time_step * dz);
    return z_next;
  }

  row_vector x_z_interp(row_vector x, row_vector z, real I1, real time_step, real dt,
			row_vector x0, matrix SC, real tau0) {
    int nn = num_elements(x);
    row_vector[2*nn] x_z_t;
    row_vector[nn] x_t;
    row_vector[nn] z_t;
    real nsteps = floor(time_step/dt);
    real step_count = 0;
    /* print("nsteps:",nsteps); */
    x_t = x;
    z_t = z;
    while(step_count != nsteps){
      x_t = x_step(x_t, z_t, I1, dt);
      z_t = z_step(x_t, z_t, x0, SC, dt, tau0);
      step_count += 1;
    }
    x_z_t[1:nn] = x_t;
    x_z_t[nn+1:2*nn] = z_t;
    return x_z_t;
  }
}

data {
  int nn;
  int ns;
  int nt;
  real I1;
  /* real tau0; */
  /* real time_step; */
  real dt;

  matrix[ns,nn] gain;
  matrix<lower=0.0, upper=1.0>[nn, nn] SC;

  // Hyperparameters
  /* row_vector[ns] mu_epsilon_slp; */
  /* row_vector[ns] mu_epsilon_snsr_pwr; */

  // Modelled data
  row_vector[ns] slp[nt]; //seeg log power
  row_vector[ns] snsr_pwr; //seeg sensor power
}

parameters {
  row_vector[nn] x0_star;
  row_vector[nn] x_init_star;
  row_vector[nn] z_init_star;
  real amplitude_star;
  real offset;
  real time_step_star;
  real K_star;
  real tau0_star;
  //  matrix<lower=0.0, upper=10.0>[nn, nn] FC;
  real epsilon_slp_star;
  real epsilon_snsr_pwr_star;
}

transformed parameters{
  row_vector[nn] x0 = -2.5 + x0_star;
  row_vector[nn] x_init = -2.0 + x_init_star;
  row_vector[nn] z_init = 3.0 + z_init_star;
  real amplitude = exp(pow(1.0, 2) + log(1.0) + 1.0*amplitude_star);
  real time_step = exp(pow(1.0, 2) + log(0.1) + 1.0*time_step_star);
  real tau0 = exp(pow(1.0, 2) + log(30.0) + 1.0*tau0_star);
  real K = exp(pow(1.0, 2) + log(1.0) + 1.0*K_star);
  real epsilon_slp = exp(pow(1.0, 2) + log(1.0) + 1.0*epsilon_slp_star);
  real epsilon_snsr_pwr = exp(pow(1.0, 2) + log(10.0) + 1.0*epsilon_snsr_pwr_star);
  /* row_vector epsilon_slp = exp(pow(0.1, 2) + log(mu_epsilon_slp) + 0.1*epsilon_slp_star); */
  /* row_vector epsilon_snsr_pwr = exp(pow(0.1, 2) + log(mu_epsilon_snsr_pwr) + 0.1*epsilon_snsr_pwr_star); */

  // Euler integration of the epileptor without noise 
  row_vector[2*nn] x_z_t;
  row_vector[nn] x[nt];
  row_vector[nn] z[nt];
  row_vector[ns] mu_slp[nt];
  row_vector[ns] mu_snsr_pwr = rep_row_vector(0, ns);
  /* print(time_step); */
  for (t in 1:nt) {
    if(t ==1)
      x_z_t = x_z_interp(x_init, z_init, I1, time_step, dt, x0, K*SC, tau0);
    else
      x_z_t = x_z_interp(x[t-1], z[t-1], I1, time_step, dt, x0, K*SC, tau0);
    x[t] = x_z_t[1:nn];
    z[t] = x_z_t[nn+1:2*nn];
    mu_slp[t] = amplitude * (log(gain * exp(x[t])')' + offset);
    for (i in 1:ns){
      mu_snsr_pwr[i] += pow(mu_slp[t][i], 2);
    }
  }
}

model {
  x0_star ~ normal(0, 1.0);
  amplitude_star ~ normal(0, 1.0);
  offset ~ normal(0, 1.0);
  /* for (i in 1:nn){ */
  /*   for (j in 1:nn){ */
  /*     FC[i,j] ~ normal(K*SC[i,j], 0.01); */
  /*   } */
  /* } */
  x_init_star ~ normal(0, 1.0);
  z_init_star ~ normal(0, 1.0);
  time_step_star ~ normal(0, 1.0);
  tau0_star ~ normal(0, 1.0);
  K_star ~ normal(0, 1.0);
  epsilon_slp_star ~ normal(0, 1.0);
  epsilon_snsr_pwr_star ~ normal(0, 1.0);
  for (t in 1:nt) {
    slp[t] ~ normal(mu_slp[t], epsilon_slp);
  }
  snsr_pwr ~ normal(mu_snsr_pwr, epsilon_snsr_pwr);
}

generated quantities {
}
