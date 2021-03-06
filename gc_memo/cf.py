"""
`cf.py` contains all required simulation parameters which can be altered
by the user as well as some information necessary for modelling antibody
mutation and binding.

Basic timestep is two hours --> give all rates and durations in units of 2 hrs!
"""
from __future__ import division
from past.utils import old_div
import numpy as np
import math

"""
timeframe and infection schedule
"""
endtime = 30*12  # give first factor in days, multiply by timesteps per day
tinf = [0*12]  # as above for every infection timepoint
dose = [1]  # fraction of maximum dose per infection timepoint

tdecay = 2*12  # decay constant of the Ag in the system assuming exp decay
p_base = 0.005  # base meeting probability per free Bcell and timestep


"""
form of the GC
"""
tmax = 7*12  # day until which GC stays at maximum size
LFdecay = 10*12  # decay constant of LFs after reaching max


"""
simulation size information
"""
nGCs = 1  # number of GCs considered
nLFs = 25  # number of limiting factors per GC
naive_pool = 1000*nGCs  # size of the naive precursor pool
memory_pool = 100*nGCs  # size of the initial unspecific memory pool

R = int(math.pow(10, 6))  # size of random number array chunks
# (purely technical information)


"""
time dynamics
"""
tmigration = 3*12  # time delay between Bcell activation and GCentry
tAID = 3*12  # time necessary between entering GC and onset of mutations
thelp = 1  # time necessary to receive enough survival signals to move on
tdiv = 4  # time necessary for division
tdiff = 4  # time necessary for differentiation and exit
tlifeGC = 4  # maximum survival time in the waiting area
tlifeN = 14*12  # lifetime of free naive cells
tsecret = 1 # time necessary for PC to start producing antibodies

recycle = 0.9  # fraction of cells that choose to divide and recycle
PCexport = 0.5  # fraction of cells that become PCs and not memory upon exit


"""
AbAg binding model
"""
nkey = 10  # length of Ab hot spot vectors (number of amino acids)
lAg = nkey  # length of Ag epitope vectors (number of amino acids)
lAb = 220 - nkey  # length of Ab V_heavy and V_light non-hotspot area

thr = 0.6  # minimum normalised binding energy for participation std=0.6
upperlim = 1  # maximum binding energy of newly produced cells


p_err_FWR = 0.003  # error probability per codon*div in the non-key part
p_err_CDR = 0.003  # error probability per codon*div in the key-part

p_death_FWR = 0.5  # probability that replacement mutation in FWR is deathly
p_block_FWR = 0.55  # probability that a non-lethal FWR mutation blocks AM

Elow = -11.5  # energy of lower detection limit in kT (K = 10^-5 mol/l)
Ehigh = -20.7  # energy of higher detection limit in kT (K = 10^-9 mol/l)

m = old_div((Ehigh-Elow),(1-thr))  # gradient of energy trafo
y0 = -m*thr+Elow

# K_D [mol/l]   <-->    Delta G [kT]
# 10^-5         <-->    -11.5
# 10^-6         <-->    -13.8
# 10^-7         <-->    -16.1
# 10^-8         <-->    -18.4
# 10^-9         <-->    -20.7
# 10^-10        <-->    -23.0

# for transformation between these, use:
# dG = math.log(K_D)
# K_D = math.exp(dG)


def E2KD(Ebind):
    """ For transforming individual normalised binding energy to KD."""
    dG = y0+m*Ebind
    KD = np.exp(dG)
    return KD


"""
Kinetic model and antibody feedback
"""

act_mode = "affinity" # how to activate cells: 'uniform' for random activation, 'affinity' for affinity-based

ab_secretion_rate = 2.1 * (10 ** -17) * 2 # [mol] antibodies secreted by 1 plasma cell per timestep (2 h)
blood_volume = 5 # [l]
PC_lifespan = 30 * 12 # [timesteps] average short-lived PC lifespan
ab_halflife = 20.0 / 2 # [timesteps] pharmacological lifespan of IgG

def ab_conc_now(t_secr_start, tnow):
    t = np.array(range(tnow - t_secr_start + 1))
    ab_per_t = ab_secretion_rate * 0.5 ** (t / ab_halflife)
    return ab_per_t.sum() / blood_volume


"""
amino acid transition and generation probabilities
"""
# amino acid generation probabilities due to number of codons per a.a.
gp20 = np.array([0.03278689, 0.01639344, 0.03278689, 0.04918033, 0.09836066,
                 0.06557377, 0.01639344, 0.03278689, 0.06557377, 0.06557377,
                 0.06557377, 0.09836066, 0.03278689, 0.03278689, 0.03278689,
                 0.03278689, 0.03278689, 0.09836066, 0.03278689, 0.06557377])

cumprob20 = np.cumsum(gp20)

# transition probabilities between codons for one random bp change due to
# genetic code, last coloumn contains probabilities for changing to STOP codons

tp20 = np.array([[ 0.11111111,  0.        ,  0.11111111,  0.        ,  0.,
         0.        ,  0.11111111,  0.11111111,  0.        ,  0.11111111,
         0.        ,  0.22222222,  0.        ,  0.        ,  0.        ,
         0.        ,  0.        ,  0.11111111,  0.        ,  0.        ,
         0.11111111],
       [ 0.        ,  0.        ,  0.        ,  0.33333333,  0.22222222,
         0.11111111,  0.        ,  0.        ,  0.        ,  0.        ,
         0.11111111,  0.        ,  0.        ,  0.        ,  0.        ,
         0.        ,  0.        ,  0.11111111,  0.11111111,  0.        ,
         0.        ],
       [ 0.11111111,  0.        ,  0.11111111,  0.11111111,  0.33333333,
         0.11111111,  0.        ,  0.11111111,  0.        ,  0.        ,
         0.        ,  0.11111111,  0.        ,  0.        ,  0.        ,
         0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.        ],
       [ 0.        ,  0.11111111,  0.07407407,  0.22222222,  0.14814815,
         0.11111111,  0.        ,  0.        ,  0.        ,  0.        ,
         0.11111111,  0.07407407,  0.        ,  0.07407407,  0.        ,
         0.        ,  0.        ,  0.03703704,  0.03703704,  0.        ,
         0.        ],
       [ 0.        ,  0.03703704,  0.11111111,  0.07407407,  0.33333333,
         0.11111111,  0.01851852,  0.        ,  0.        ,  0.        ,
         0.        ,  0.03703704,  0.03703704,  0.        ,  0.        ,
         0.        ,  0.03703704,  0.07407407,  0.        ,  0.07407407,
         0.05555556],
       [ 0.        ,  0.02777778,  0.05555556,  0.08333333,  0.16666667,
         0.33333333,  0.        ,  0.        ,  0.11111111,  0.11111111,
         0.        ,  0.        ,  0.        ,  0.        ,  0.05555556,
         0.05555556,  0.        ,  0.        ,  0.        ,  0.        ,
         0.        ],
       [ 0.22222222,  0.        ,  0.        ,  0.        ,  0.11111111,
         0.        ,  0.        ,  0.        ,  0.        ,  0.11111111,
         0.        ,  0.11111111,  0.        ,  0.        ,  0.        ,
         0.        ,  0.        ,  0.22222222,  0.        ,  0.        ,
         0.22222222],
       [ 0.11111111,  0.        ,  0.11111111,  0.        ,  0.        ,
         0.        ,  0.        ,  0.11111111,  0.        ,  0.        ,
         0.        ,  0.11111111,  0.        ,  0.11111111,  0.        ,
         0.11111111,  0.11111111,  0.        ,  0.        ,  0.        ,
         0.22222222],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.11111111,  0.        ,  0.        ,  0.33333333,  0.11111111,
         0.11111111,  0.11111111,  0.        ,  0.        ,  0.05555556,
         0.05555556,  0.        ,  0.        ,  0.        ,  0.11111111,
         0.        ],
       [ 0.05555556,  0.        ,  0.        ,  0.        ,  0.        ,
         0.11111111,  0.02777778,  0.        ,  0.11111111,  0.33333333,
         0.        ,  0.05555556,  0.        ,  0.        ,  0.05555556,
         0.05555556,  0.        ,  0.16666667,  0.        ,  0.        ,
         0.02777778],
       [ 0.        ,  0.02777778,  0.        ,  0.08333333,  0.        ,
         0.        ,  0.        ,  0.        ,  0.11111111,  0.        ,
         0.33333333,  0.16666667,  0.        ,  0.05555556,  0.        ,
         0.        ,  0.        ,  0.05555556,  0.05555556,  0.11111111,
         0.        ],
       [ 0.07407407,  0.        ,  0.03703704,  0.03703704,  0.03703704,
         0.        ,  0.01851852,  0.03703704,  0.07407407,  0.03703704,
         0.11111111,  0.25925926,  0.        ,  0.03703704,  0.        ,
         0.        ,  0.        ,  0.11111111,  0.        ,  0.07407407,
         0.05555556],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.11111111,
         0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.        ,  0.        ,  0.11111111,  0.        ,  0.11111111,
         0.        ,  0.22222222,  0.11111111,  0.11111111,  0.11111111,
         0.11111111],
       [ 0.        ,  0.        ,  0.        ,  0.11111111,  0.        ,
         0.        ,  0.        ,  0.11111111,  0.        ,  0.        ,
         0.11111111,  0.11111111,  0.        ,  0.11111111,  0.        ,
         0.11111111,  0.11111111,  0.        ,  0.22222222,  0.        ,
         0.        ],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.11111111,  0.        ,  0.        ,  0.11111111,  0.11111111,
         0.        ,  0.        ,  0.11111111,  0.        ,  0.11111111,
         0.22222222,  0.        ,  0.        ,  0.11111111,  0.        ,
         0.11111111],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.11111111,  0.        ,  0.11111111,  0.11111111,  0.11111111,
         0.        ,  0.        ,  0.        ,  0.11111111,  0.22222222,
         0.11111111,  0.11111111,  0.        ,  0.        ,  0.        ,
         0.        ],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.11111111,
         0.        ,  0.        ,  0.11111111,  0.        ,  0.        ,
         0.        ,  0.        ,  0.22222222,  0.11111111,  0.        ,
         0.11111111,  0.11111111,  0.11111111,  0.        ,  0.11111111,
         0.        ],
       [ 0.03703704,  0.01851852,  0.        ,  0.01851852,  0.07407407,
         0.        ,  0.03703704,  0.        ,  0.        ,  0.11111111,
         0.03703704,  0.11111111,  0.03703704,  0.        ,  0.        ,
         0.        ,  0.03703704,  0.33333333,  0.03703704,  0.07407407,
         0.03703704],
       [ 0.        ,  0.05555556,  0.        ,  0.05555556,  0.        ,
         0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.11111111,  0.        ,  0.11111111,  0.22222222,  0.11111111,
         0.        ,  0.        ,  0.11111111,  0.11111111,  0.        ,
         0.11111111],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.11111111,
         0.        ,  0.        ,  0.        ,  0.11111111,  0.        ,
         0.11111111,  0.11111111,  0.05555556,  0.        ,  0.        ,
         0.        ,  0.05555556,  0.11111111,  0.        ,  0.33333333,
         0.        ]])


# Thomas-Dill binding energy matrix
TD20 = np.array([[-1.79, -1.23, -0.98, -0.48, -0.69, -0.94, -0.3 , -0.96, -0.3 , -0.42, -0.38, -0.2 , -0.49, -0.32,  0.04,  0.55, -0.82, -0.4 ,  0.  ,  0.07],
                 [-1.23,  0.36, -1.03, -0.41, -0.31, -0.94, -0.07, -1.1 ,  0.05,  0.  ,  0.06, -0.47, -0.54,  0.31,  0.02,  1.07, -0.35, -0.43,  0.55, -0.25],
                 [-0.98, -1.03, -0.61, -0.66, -1.02, -0.78, -0.89, -0.82, -0.05,  0.21, -0.19,  0.14,  0.1 , -0.02,  0.19,  0.2 , -0.75, -0.22, -0.17, -0.43],
                 [-0.48, -0.41, -0.66, -0.71, -1.04, -0.98, -0.89, -0.87, -0.64,  0.4 , -0.29, -0.13, -0.39,  0.39, -0.2 ,  0.04, -0.52, -0.08, -0.26,  0.25],
                 [-0.69, -0.31, -1.02, -1.04, -1.14, -1.03, -0.97, -0.6 , -0.57, -0.08, -0.39, -0.07, -0.13, -0.1 , -0.05,  0.5 , -0.36, -0.1 ,  0.1 ,  0.09],
                 [-0.94, -0.94, -0.78, -0.98, -1.03, -1.15, -0.6 , -0.7 , -0.6 , -0.2 ,  0.06, -0.31, -0.09, -0.24, -0.02,  0.25, -0.35, -0.48, -0.08, -0.08],
                 [-0.3 , -0.07, -0.89, -0.89, -0.97, -0.6 ,  0.02, -0.99, -0.08, -0.14,  0.07, -0.2 ,  0.4 , -0.68,  0.32,  0.24, -0.41, -0.78, -0.3 , -0.44],
                 [-0.96, -1.1 , -0.82, -0.87, -0.6 , -0.7 , -0.99,  0.35, -0.37, -0.32, -0.23,  0.25, -0.39, -0.74,  0.22,  0.11, -0.67,  0.21, -0.2 , -0.45],
                 [-0.3 ,  0.05, -0.05, -0.64, -0.57, -0.6 , -0.08, -0.37, -0.08, -0.09, -0.22, -0.01, -0.11, -0.14,  0.03,  0.1 , -0.15,  0.07,  0.  ,  0.41],
                 [-0.42,  0.  ,  0.21,  0.4 , -0.08, -0.2 , -0.14, -0.32, -0.09,  0.04,  0.13, -0.04,  0.12, -0.18,  0.4 , -0.06,  0.  , -0.15,  0.1 ,  0.4 ],
                 [-0.38,  0.06, -0.19, -0.29, -0.39,  0.06,  0.07, -0.23, -0.22,  0.13,  0.26,  0.05, -0.17, -0.27,  0.15, -0.03, -0.27, -0.17,  0.09,  0.36],
                 [-0.2 , -0.47,  0.14, -0.13, -0.07, -0.31, -0.2 ,  0.25, -0.01, -0.04,  0.05, -0.13,  0.4 ,  0.37,  0.3 , -0.09, -0.59,  0.61,  0.18,  0.44],
                 [-0.49, -0.54,  0.1 , -0.39, -0.13, -0.09,  0.4 , -0.39, -0.11,  0.12, -0.17,  0.4 , -0.08, -0.05,  0.62,  0.46,  0.05,  0.62,  0.04, -0.21],
                 [-0.32,  0.31, -0.02,  0.39, -0.1 , -0.24, -0.68, -0.74, -0.14, -0.18, -0.27,  0.37, -0.05, -0.86, -0.25, -0.12,  0.06,  0.04,  0.18,  0.11],
                 [ 0.04,  0.02,  0.19, -0.2 , -0.05, -0.02,  0.32,  0.22,  0.03,  0.4 ,  0.15,  0.3 ,  0.62, -0.25,  0.21,  0.68, -0.53, -0.26, -0.09,  0.84],
                 [ 0.55,  1.07,  0.2 ,  0.04,  0.5 ,  0.25,  0.24,  0.11,  0.1 , -0.06, -0.03, -0.09,  0.46, -0.12,  0.68,  0.6 , -0.06, -0.15, -0.09,  0.84],
                 [-0.82, -0.35, -0.75, -0.52, -0.36, -0.35, -0.41, -0.67, -0.15,  0.  , -0.27, -0.59,  0.05,  0.06, -0.53, -0.06,  0.14, -0.01,  0.14, -0.22],
                 [-0.4 , -0.43, -0.22, -0.08, -0.1 , -0.48, -0.78,  0.21,  0.07, -0.15, -0.17,  0.61,  0.62,  0.04, -0.26, -0.15, -0.01,  0.23,  0.3 , -0.02],
                 [ 0.  ,  0.55, -0.17, -0.26,  0.1 , -0.08, -0.3 , -0.2 ,  0.  ,  0.1 ,  0.09,  0.18,  0.04,  0.18, -0.09, -0.09,  0.14,  0.3 ,  1.45,  0.51],
                 [ 0.07, -0.25, -0.43,  0.25,  0.09, -0.08, -0.44, -0.45,  0.41,  0.4 ,  0.36,  0.44, -0.21,  0.11,  0.84,  0.84, -0.22, -0.02,  0.51,  0.28]])


# complete alphabet (order like in Dill and Thomas for 20 classes)

cAA = [['C'],
       ['M'],
       ['F'],
       ['I'],
       ['L'],
       ['V'],
       ['W'],
       ['Y'],
       ['A'],
       ['G'],
       ['T'],
       ['S'],
       ['Q'],
       ['N'],
       ['E'],
       ['D'],
       ['H'],
       ['R'],
       ['K'],
       ['P']]
