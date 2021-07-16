# privacy_engineering_cw1

Privacy Engineering coursework 1

This is a demonstration of the BGW Secret Sharing protocol running on a single machine for multiple parties in separate processes.

## Installation

The following package is required for communication:

```bash
pip install pyzmq
```

## Usage
Run the following command from a Mac or Linux terminal:

```bash
make sort
```

## Selecting a circuit
Modify `circuit.py` and change the `CIRCUIT` variable at the top of the file.  Options are:

- 1: 6 party multiplication and addition circuit.
- 2: N party calculation of factorial (or product of each party's secret).
- 3: 5 party addition circuit used for testing.
- 4: 3 party multiplication circuit used for testing.
- 5: 3 party multiplication and addition circuit used for testing.
- 6: N party summation circuit
- 7: N party calculation of exponential (or product of each party's secret)
- 8: N party calculation of mean squared error loss function