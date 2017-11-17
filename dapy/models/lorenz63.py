"""Three-dimensional model with chaotic non-linear dynamics.

Model originally proposed in:

> Lorenz, Edward Norton (1963).
> Deterministic nonperiodic flow.
> Journal of the Atmospheric Sciences. 20 (2): 130–141.
"""

import numpy as np
from dapy.models.base import (
    DiagonalGaussianIntegratorModel, inherit_docstrings)
from dapy.models.lorenz63integrator import Lorenz63Integrator


@inherit_docstrings
class Lorenz63Model(DiagonalGaussianIntegratorModel):
    """Three-dimensional model with chaotic non-linear dynamics

    Model dynamics defined by the system of ODEs

        dz[0]/dt = sigma * (z[1] - z[0]),
        dz[1]/dt = z[0] * (rho - z[2]) - z[1],
        dz[2]/dt = z[0] * z[1] - beta * z[2].

    An implicit mid-point method (with fixed point iteration to solve for the
    update) is used here to integrate the system from an initial state with
    a diagonal Gaussian distribution. The observations are assumed to be
    generated given states generated by integrating forward the dynamics by a
    fixed time interval (the product of the intergrator time step and the
    number of steps per update). Optionally as well as the numerical
    integration based state update, additive Gaussian noise may be also
    included in these fixed interval state updates to represent the
    accumulated model error. The observations are assumed to be computed as a
    possibly non-linear function of the state plus additive Gaussian
    observation noise.

    References:
        Lorenz, Edward Norton (1963). Deterministic nonperiodic flow.
        Journal of the Atmospheric Sciences. 20 (2): 130–141.
    """

    def __init__(self, rng, init_state_mean=1., init_state_std=0.05,
                 state_noise_std=None, observation_func=lambda z: z,
                 obser_noise_std=5., sigma=10., rho=28., beta=8./3., dt=0.01,
                 n_steps_per_update=10, tol=1e-8, max_iters=100, n_threads=4):
        """
        Args:
            rng (RandomState): Numpy RandomState random number generator.
            init_state_mean (float or array): Initial state distribution mean.
                Either a scalar or array of shape `(3,)`.
            init_state_std (float or array): Initial state distribution
                standard deviation. Either a scalar or array of shape `(3,)`.
            state_noise_std (float or array): Standard deviation of additive
                Gaussian noise in state update. Either a scalar or array of
                shape `(3,)`. Noise in each dimension assumed to be independent
                i.e. a diagonal noise covariance. If zero or None deterministic
                dynamics are assumed.
            observation_func (function): Function mapping from states to
                 observations, prior to addition of observation noise. Defaults
                 to identity function.
            obser_noise_std (float): Standard deviation of additive Gaussian
                noise in observations. Either a scalar or array of shape
                `(3,)`. Noise in each dimension assumed to be independent
                i.e. a diagonal noise covariance.
            sigma (float): Coefficient in non-linear state update.
            rho (float): Coefficient in non-linear state update.
            beta (float): Coefficient in non-linear state update.
            dt (float): Time step for implicit mid-point integrator.
            n_steps_per_update (int): Number of integrator time-steps between
                successive observations and generated states.
            tol (float): Convergence tolerance for fixed point iteration.
            max_iters (int): Maximum number of iterations in fixed-point
                iterative solution of implicit update. ConvergenceError
                exception raised if iteration fails to converge within
                specified number.
            n_threads (int): Number of threads to parallelise model dynamics
                integration over.
        """
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.dt = dt
        self.n_steps_per_update = n_steps_per_update
        self.tol = tol
        self.max_iters = max_iters
        self.n_threads = n_threads
        self.observation_func = observation_func
        dim_x = observation_func(np.zeros(3)).shape[0]
        integrator = Lorenz63Integrator(
            sigma=sigma, rho=rho, beta=beta, dt=dt, tol=tol,
            n_steps_per_update=n_steps_per_update, max_iters=max_iters,
            n_threads=n_threads
        )
        super(Lorenz63Model, self).__init__(
            integrator=integrator, dim_z=3, dim_x=dim_x, rng=rng,
            init_state_mean=init_state_mean, init_state_std=init_state_std,
            state_noise_std=state_noise_std, obser_noise_std=obser_noise_std
        )
