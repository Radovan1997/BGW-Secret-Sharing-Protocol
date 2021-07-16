# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020
# Radovan, rv20@ic.ac.uk, November 2020
# Jamie Salter, jas20@ic.ac.uk, November 2020


# Circuit below to evalute
CIRCUIT = 1

# Gate types
INP, ADD, MUL = (0,1,2)

# Define MPC Function as an addition/multiplication circuit. INPut gates 
# precede ADD/MUL gates. ADD/MUL gates are defined in evaluation order. 
# By convention the final wire is considerd the circuit's output wire.

if CIRCUIT == 1: 	# example in Smart
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 2

  PRIVATE_VALUES = {1:20, 2:40, 3:21, 4:31, 5:1, 6:71}

  def function(x):	# function being evaluated by parties
    return (x[1]*x[2] + x[3]*x[4] + x[5]*x[6]) % PRIME

  GATES = {
    1:  (INP, 7,1),
    2:  (INP, 7,2),
    3:  (INP, 8,1),
    4:  (INP, 8,2),
    5:  (INP, 9,1),
    6:  (INP, 9,2),
    7:  (MUL, 10,1),
    8:  (MUL, 10,2),
    9:  (MUL, 11,1),
    10: (ADD, 11,2),
    11: (ADD, 12,1),  	# (12,1) is circuit output wire
  }

elif CIRCUIT == 2:	# factorial tree for 2^n parties
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME = 100_003
  # PRIME = 1_000_000_007
  # PRIME = 35742549198872617291353508656626642567  # Large Bell prime

  # degree of polynominal - T in slides
  DEGREE = 2

  INPUTS = 2 ** 3
  PRIVATE_VALUES = {k: k for k in range(1, INPUTS+1)}

  def function(x):	# function being evaluated by parties
    product = 1
    for value in x.values(): product = (product * value) % PRIME
    return product

  GATES = {}

  def tree(next_gate, n_gates):
    global GATES
    if n_gates >= 1:
      kind = INP if next_gate == 1 else MUL
      output_gate = next_gate + n_gates
      last_gate = output_gate - 1
      for g in range(next_gate, output_gate, 2):
        GATES[g]   = (kind, output_gate, 1)
        if g < last_gate:
          GATES[g+1] = (kind, output_gate, 2)
        output_gate += 1
      tree(next_gate + n_gates, n_gates // 2)

  tree(1, INPUTS)

# ___________________________________________________________________________
elif CIRCUIT == 3:	# Basic AND gate
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 2

  PRIVATE_VALUES = {1:99, 2:50, 3:55, 4:10, 5:13}

  def function(x):	# function being evaluated by parties
    return (x[1] + x[2] + x[3] + x[4] + x[5]) % PRIME

  GATES = {
    1:  (INP, 6,1),
    2:  (INP, 6,2),
    3:  (INP, 7,1),
    4:  (INP, 7,2),
    5:  (INP, 9,1),
    6:  (ADD, 8,1),
    7:  (ADD, 8,2),
    8:  (ADD, 9,2),
    9:  (ADD, 10,1)
  }

  # ___________________________________________________________________________
elif CIRCUIT == 4:	# Basic MUL gate
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 1

  PRIVATE_VALUES = {1:3, 2:4, 3:5}

  def function(x):	# function being evaluated by parties
    return (x[1] * x[2] * x[3]) % PRIME

  GATES = {
    1:  (INP, 4,1),
    2:  (INP, 4,2),
    3:  (INP, 5,1),
    4:  (MUL, 5,2),
    5:  (MUL, 6,1) # (6,1) is circuit output wire
  }

  # ___________________________________________________________________________
elif CIRCUIT == 5:	# Basic MUL gate 2
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 1

  PRIVATE_VALUES = {1:3, 2:4, 3:5}

  def function(x):	# function being evaluated by parties
    return ((x[1] + x[2]) * x[3]) % PRIME

  GATES = {
    1:  (INP, 4,1),
    2:  (INP, 4,2),
    3:  (INP, 5,1),
    4:  (ADD, 5,2),
    5:  (MUL, 6,1) # (6,1) is circuit output wire
  }

elif CIRCUIT == 6:	# SUM CIRCUIT 
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 1

  # sum of range up to input modded by PRIME
  INPUT = 20 
  PRIVATE_VALUES = {k: k for k in range(1,INPUT+1)} # takes in all values in the range up to INPUT

  def function(x):
    rsum = 0
    for n in x.values():
      rsum += n
    
    return rsum % PRIME
  
  def make_gates(private):
    gates = {}
    size = len(private)

    gates[1] = (INP, size+1, 1)
    gates[2] = (INP, size+1, 1)
    
    for i in range(3,size+1):
      gates[i] = (INP, size + i -1, 1)
    
    for i in range(size+1, 2*size):
      gates[i] = (ADD, i+1, 1)
    
    return gates
  
  GATES = make_gates(PRIVATE_VALUES)

# _______________________________________________
# This circuit takes in two values BASE and EXP and return BASE ** EXP
elif CIRCUIT == 7:
  PRIME = 101 # PRIME NUMBER we mod over
  DEGREE = 1

  BASE = 3 # BASE value 
  EXP = 4 # Exponent value

  PRIVATE_VALUES = {k: BASE for k in range(1,EXP+1)} # creates EXP copies of BASE to make BASE ** EXP

  def function(x):
    product = 1
    for n in x.values():
      product *=n

    return product % PRIME
  
  def make_gates(private):
    gates = {} # Initialize our circuit to empty
    size = len(private) # Need to know the size of PRIVATE_VALUES since it is EXP

    gates[1] = (INP, size+1, 1)
    gates[2] = (INP, size+1, 1)
    
    for i in range(3,size+1):
      gates[i] = (INP, size + i -1, 1) # SET Input gates 
    
    # Set multiplication gates that send 
    # their result to the next multiplication gate
    for i in range(size+1, 2*size):
      gates[i] = (MUL, i+1, 1)
    
    return gates
  
  GATES = make_gates(PRIVATE_VALUES) # Assign GATES the value of the circuit

# _______________________________________________
# Calculate mean squared error loss function sum
elif CIRCUIT == 8: 

  # target = 2x + 1
  # estimate = 3x + 9
  num_points = 2

  DEGREE = num_points
  PRIME = 100_003

  # Generate values for target function
  target =  {x: (2*x + 1) for x in range(1, num_points+1)}

  # Generate values for estimates
  estimate = {x: (3*x + 9) for x in range(1, num_points+1)}

  PRIVATE_VALUES = {}

  # Create private values by mixing target, estimate and -1 
  for i in target:
    PRIVATE_VALUES[3*i -2] = target[i]
    PRIVATE_VALUES[3*i+1 -2] = estimate[i]
    PRIVATE_VALUES[3*i+2 -2] = -1
  
  # Our function is a squared error loss function
  def function(x):
    loss_sum = 0
    for i in range(1,len(x)+1):
      if (i % 3 == 1):
        loss_sum = (loss_sum + (x[i] - x[i+1])**2)
    
    return loss_sum % PRIME
  
  def make_circuit(private):
    """
    Takes in private values and generates a circuit to evaluate
    squared error of estimate on target

    The design of the circuit follows a pattern

    For each pair there:
       are 3 input gates
       5 gates used to create the pair error 
    
    Since each pair uses the same sub circuit to calculate it's error
    we can increment by 5 to get the next gate that needs similar behaviour
    
    After that we need to sum the errors together
    There are len(private)/3 pairs to count 

    We create gates for that 
    Those gates start at len(private) * (3 + 5) + 1

    """
    
    # determines the amout of points
    # points are grouped in 3 (target_value, estimate, -1)
    size = int(len(private)/3)
    gates = {} # initialize gates dictionary

    # used to see where each target estimate pair has been counted 
    # then gates are numbered after adders + 1 forward to sum errors together
    adders = size*8

    # determines how many pairs have been counted
    end_counter = 0
    psize = len(private) #input size


    # Creating input gates
    for i in range(1, psize+1):
      if (i % 3 == 1):
        gates[i] = (INP, [(psize+2 + (i//3)*5, 1), (psize+4 + (i//3)*5, 1)])
      
      if (i % 3 == 2):
        gates[i] = (INP, [(psize+1 + (i//3)*5, 1), (psize+3 + (i//3)*5, 1)])
      
      if (i %3 == 0):
        gates[i] = (INP, [(psize+1 + (i//3-1)*5, 1), (psize+3 + (i//3-1)*5, 1)])
    
    # Creating gates that calculate error for each pair
    for i in range(psize+1,size*8+1):

      if ((i-psize)%5 == 1):
        gates[i] = (MUL, i+1, 1)
      
      if ((i-psize)%5 == 2):
        gates[i] = (ADD, i+3,1) 
      
      if ((i-psize)%5 == 3):
        gates[i] = (MUL, i+1, 1)
      
      if ((i-psize)%5 == 4):
        gates[i] = (ADD, i+1, 1)
      
      if ((i-psize)%5 == 0):
        end_counter += 1
        if (end_counter == 1 or end_counter == 2):
          gates[i] = (MUL, adders+1,1)
        else:
          gates[i] = (MUL, adders+end_counter-1, 1)
  
    # Creating the gates that sum the errors together
    for x in range(adders+1, adders + end_counter):
      gates[x] = (ADD, x+1, 1)
    
    return gates
  
  GATES = make_circuit(PRIVATE_VALUES)
  #print(GATES)
   

#_____________________________________________________________
# true function result - used to check result from MPC circuit
FUNCTION_RESULT = function(PRIVATE_VALUES)

N_GATES     = len(GATES)
N_PARTIES   = len(PRIVATE_VALUES)
ALL_PARTIES = range(1, N_PARTIES+1)
ALL_DEGREES = range(1, DEGREE+1)

assert PRIME > N_PARTIES, "Prime > N failed :-("
assert 2*DEGREE < N_PARTIES, "2T < N failed :-("

# Various Primes 
# PRIME = 11
# PRIME = 101
# PRIME = 1_009
# PRIME = 10_007
# PRIME = 100_003
# PRIME = 1_000_003 
# PRIME = 1_000_000_007
# PRIME = 35742549198872617291353508656626642567  # Large Bell prime


