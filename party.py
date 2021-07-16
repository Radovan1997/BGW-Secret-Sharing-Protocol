# Radovan, rv20@ic.ac.uk, November 2020
# Jamie Salter, jas20@ic.ac.uk, November 2020

import random     # seed
import subprocess # Popen
import sys        # argv
import time       # sleep
import math
from collections import defaultdict

from circuit import ALL_PARTIES, CIRCUIT, N_PARTIES, PRIVATE_VALUES, GATES, INP, ADD, MUL, PRIME, FUNCTION_RESULT, DEGREE
from config  import LOCAL, MAX_TIME, PKILL_PATTERN, REPEATABLE_RANDOM_NUMBERS
import log
from network import Network
from modprime import add, mod, mul

class BgwProtocol:

    def __init__(self, party_no, private_value, network):
        log.write(f"Started BGW for party {party_no} with private value {private_value}")

        self.network = network
        self.secret = private_value
        self.party_no = party_no

        # Go through and process all the gates
        self.process_gates()

    def process_gates(self):
        for gate in GATES:
            if GATES[gate][0] == INP and gate == self.party_no:
                log.debug(f"Gate {gate}: START processing INP matching this party number", 1)

                # Split our secret and share to all parties
                self.split_and_send_shares(self.secret, gate)
                log.debug(f"Gate {gate}: END processing INP", 1)

            if GATES[gate][0] == ADD:
                log.debug(f"Gate {gate}: START processing ADD", 1)

                # Inputs either come from previous input gates or we sent to ourselves
                inputs = self.get_inputs(gate)

                # Calculate the output
                output = add(inputs[0], inputs[1])
                log.debug(f"Gate {gate}: Output of ADD is {output}", 1)

                # Send the output to ourselves for further processing
                self.send_output(output, gate)
                log.debug(f"Gate {gate}: END processing ADD", 1)
                
            if GATES[gate][0] == MUL:
                log.debug(f"Gate {gate}: START processing MULT", 1)
                inputs = self.get_inputs(gate)

                # Calculate the output
                output = mul(inputs[0], inputs[1])
                log.debug(f"Gate {gate}: Internal result of multiplication is {output}", 1)

                # Split and sub-share this share of the multiplication
                self.split_and_send_shares(output, gate)

                # Receive shares from everyone else
                party_shares = {}
                for party in ALL_PARTIES:
                    # Set the clear flag to true to clear this from buffer
                    party_shares[party] = self.network.receive_share(party, gate, True)

                # Get the result of the multiplication
                output = self.get_secret(party_shares, N_PARTIES)
                log.debug(f"Gate {gate}: Degree reduced output of MULT is {output}", 1)

                self.send_output(output, gate)
                log.debug(f"Gate {gate}: END Processing MULT", 1)

        # Print blank line to separate parties in the logs
        log.write('')

    def send_output(self, output, gate):
        # If this is not the last gate send this share to ourselves
        if  len(GATES[gate]) < 3 or GATES[gate][1] <= len(GATES):
            log.debug(f"Gate {gate}: Sending {output} to ourselves", 2)
            self.network.send_share(output, gate, self.party_no)
        
        # If this is the last gate
        else:
            for party in ALL_PARTIES:
                self.network.send_share(output, gate, party)
            
            party_shares = {}
            for party in ALL_PARTIES:
                party_shares[party] = self.network.receive_share(party, gate)
            log.debug(f"Gate {gate}: Party shares is {party_shares}", 2)
            
            secret = self.get_secret(party_shares)
            log.debug(f"Gate {gate}: Secret is {secret}", 2)
            
            if (secret == FUNCTION_RESULT):
                log.write(f'SUCCESS! The secret of {secret} was calculated.')
            
            else:
                log.write(f'FAIL! We calculated {secret}, but the correct value was {FUNCTION_RESULT}')

    def split_and_send_shares(self, value, src_gate):
        coefs = [0 for x in range(DEGREE)]
        for i in range(len(coefs)):
            coefs[i] = int(random.random()*(PRIME-1))
        '''
        Custom coefficients to match Smart book example
        a1 = [57.0, 93.0, 66.5, 14.5, 37.0, 93.5]
        a2 = [68.0, 95.0, 17.5, 47.5, 91.0, 0.5]
        if src_gate == 7:
            a1 = [6.5, 98.0, 45.5, 83.5, 3.5, 33.5]
            a2 = [52.5, 13.0, 30.5, 44.5, 15.5, 69.5]
        coefs = [a1[self.party_no-1], a2[self.party_no-1]]
        '''
        # Get a list of share for logging
        shares = []
        for party in ALL_PARTIES:
            share = value
            for i, c in enumerate(coefs):
                share += c*(party**(i+1))
            
            share = int(mod(share))
            self.network.send_share(share, src_gate, party)
            shares.append(share)
        log.debug(f"Gate {src_gate}: Split and sent value {value} into shares {shares} using coefficients {coefs}", 1)

    @staticmethod
    def get_lagrange(degree):
        lagrange_basis = {}
        for i in ALL_PARTIES:
            product = 1
            for j in range(1, degree + 1):
                if i == j:
                    continue
                product *= j / (j-i)
            lagrange_basis[i] = product
        return lagrange_basis

    def get_secret(self, party_shares, degree = DEGREE + 1):
        lagrange_basis = self.get_lagrange(degree)
        secret = 0
        for i in lagrange_basis:
            if i > degree:
                break
            secret += lagrange_basis[i] * party_shares[i]
        secret = int(mod(secret))
        log.debug(f"Secret = {secret} recovered from shares from each party of {party_shares}", 1)
        log.debug(f"using Lagrange basis functions of degree {degree} equal to {lagrange_basis}", 1)
        return secret

    def get_inputs(self, gate):
        inputs = []
        # Loop through every gate and find gates that input into this gate
        for gate_id, destinations in GATES.items():
            if len(destinations) == 2:
                gate_type, dest_list = destinations
                for dest in dest_list:
                    dest_gate, leg = dest
                    self.process_inputs(inputs, gate, gate_id, gate_type, dest_gate, leg)
            else:
                (gate_type, dest_gate, leg) = destinations
                self.process_inputs(inputs, gate, gate_id, gate_type, dest_gate, leg)
        log.debug(f"Gate {gate}: Inputs are {inputs}", 2)
        return inputs

    def process_inputs(self, inputs, gate, gate_id, gate_type, dest_gate, leg):
        if dest_gate == gate:
            if gate_type == INP:
                # We assume each party has an input gate with id = their party number
                # So for each input gate, the source party and source gate are the same
                inputs.append(int(self.network.receive_share(gate_id, gate_id)))
            else:
                # Get shares we've sent to ourself within the network
                inputs.append(int(self.network.receive_share(self.party_no, gate_id)))
        return inputs