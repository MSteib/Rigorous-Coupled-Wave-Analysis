import numpy as np
import matplotlib.pyplot as plt
from convolution_matrices import convmat2D as cm
from RCWA_functions import run_RCWA_simulation as rrs
import cmath
from numpy.linalg import cond

'''
RCWA testing with a metal, a dispersive medium, which means epsilon is frequency dependent.
'''

#% General Units
degrees = np.pi/180;
L0 = 1e-6; #units of microns;
eps0 = 8.854e-12*L0;
mu0 = 4*np.pi*10**-7*L0;
c0 = 1/(np.sqrt(mu0*eps0))

## lattice and material parameters
a = 0.5-1e-3;
radius = 0.1;
e_r = 12;

## Specify number of fourier orders to use:
#scalign with number of orders is pretty poor
N = 4; M = 4;

## =============== Simulation Parameters =========================
## set wavelength scanning range
#never want lattice constant and wavelength to match
wavelengths = np.linspace(1.2, 2.5,113); #500 nm to 1000 nm #be aware of Wood's Anomalies

## drude parameters
## simulating a metal suffers errors ... even with loss added
omega_p = 0.72*np.pi*1e15;
gamma = 5.5e12;

ref = list(); tran = list();
for wvlen in wavelengths:
    print('wvlen: '+str(wvlen));
    omega = 2*np.pi*c0/(wvlen); #must be in SI for eps_drude

    #sign should be positive?
    eps_drude = 1-omega_p**2/(omega**2-cmath.sqrt(-1)*omega*gamma);
    # ============== build high resolution circle ==================
    Nx = 512;
    Ny = 512;
    A = e_r* np.ones((Nx, Ny)); A = A.astype('complex')
    ci = int(Nx / 2);
    cj = int(Ny / 2);
    cr = (radius / a) * Nx;
    I, J = np.meshgrid(np.arange(A.shape[0]), np.arange(A.shape[1]));
    dist = np.sqrt((I - ci) ** 2 + (J - cj) ** 2);
    A[np.where(dist < cr)] = eps_drude;  ## A METALLIC HOLE...the fact that we have to recalculate the convolution
                                         ## for every frequency is pretty sucky...
    # plt.imshow(np.abs(A));
    # plt.show();
    ## =============== Convolution Matrices ==============
    E_r = cm.convmat2D(A, N, M)
    E_r = np.matrix(E_r)

    NM = (2 * N + 1) * (2 * M + 1);

    ## ================== GEOMETRY OF THE LAYERS AND CONVOLUTIONS ==================##
    thickness_slab = 0.2;  # in units of L0;
    ER = [E_r];
    UR = [np.matrix(np.identity(NM))];
    layer_thicknesses = [thickness_slab];  # this retains SI unit convention

    #source parameters
    theta = 0 * degrees; #%elevation angle
    phi = 0 * degrees; #%azimuthal angle

    ## incident wave polarization
    normal_vector = np.array([0, 0, -1]) #positive z points down;
    ate_vector = np.matrix([0, 1, 0]); #vector for the out of plane E-field
    #ampltidue of the te vs tm modes (which are decoupled)
    pte = 1/np.sqrt(2);
    ptm = cmath.sqrt(-1)/np.sqrt(2);

    lattice_constants = [a, a];
    e_half = [1,1];
    R,T = rrs.run_RCWA_2D(wvlen, theta, phi, ER, UR, layer_thicknesses, lattice_constants, pte, ptm, N,M, e_half)
    ref.append(R);
    tran.append(T)
    print(R);


ref = np.array(ref);
tran = np.array(tran);
absorption = 1-(ref+tran);

plt.figure();
plt.imshow(np.abs(A))

plt.figure();
plt.plot(wavelengths, ref);
plt.plot(wavelengths, tran);
plt.plot(wavelengths, 1-(ref+tran))
plt.plot(wavelengths, ref+tran+absorption);
plt.legend(('ref', 'tran', 'abs'))

plt.show()

