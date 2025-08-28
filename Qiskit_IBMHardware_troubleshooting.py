import qiskit
import qiskit_machine_learning
import qiskit_ibm_runtime
# import qiskit_aer

print('Qiskit Version :', qiskit.version.get_version_info())
print('Qiskit Machine Learning Version :', qiskit_machine_learning.__version__)
print('Qiskit-IBM-runtime Version :', qiskit_ibm_runtime.__version__)
# print('Qiskit-Aer Version :', qiskit_aer.__version__)

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter, ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit_machine_learning.neural_networks import EstimatorQNN, NeuralNetwork
from qiskit.circuit.library import U3Gate
from qiskit_machine_learning.connectors import TorchConnector
from qiskit_machine_learning.utils import algorithm_globals
# from qiskit_machine_learning.gradients import ParamShiftEstimatorGradient, SPSAEstimatorGradient
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2
# from qiskit_ibm_runtime import Sampler as RuntimeSampler

from qiskit_ibm_runtime.options import EstimatorOptions


# --- Part 1: Build the Quantum Circuit ---

# Create a Quantum Circuit with one quantum bit (qubit) and one classical bit.
# The qubit is where the quantum operations happen.
# The classical bit is where we store the measurement result.
qc = QuantumCircuit(1, 1)

# Apply an X-gate to the qubit at index 0.
# The X-gate is a quantum NOT gate; it flips the state of the qubit.
# By default, a qubit starts in the state |0>. The X-gate flips it to |1>.
qc.x(0)

# Add a measurement operation.
# This measures the state of the qubit (0) and collapses it into a classical
# state (0 or 1), which is then stored in the classical bit (0).
qc.measure(0, 0)

# You can print the circuit to visualize it in text form.
print("Quantum Circuit:")
print(qc)


try:
    print("\n--- Attempting to run on real hardware ---")
    token = 'eUWFjzNB3ODYakNACbjPCO3As_BSQiCZhJB3ltTxlKTc'
    CRN = 'crn:v1:bluemix:public:quantum-computing:us-east:a/a9b97467e1764d528c81e4fb88381d3e:3b139d2c-e5e1-4559-a1cf-c4c566338523::'
    service = QiskitRuntimeService(
        channel='ibm_quantum_platform',
        instance=CRN,
        token=token,
    )

    # Find the least busy backend that is not a simulator and has at least 1 qubit.
    backend = service.least_busy(min_num_qubits=1, simulator=False, operational=True)
    print("Least busy backend found:", backend.name)

    # Define the observable we want to measure. For a Pauli Z measurement on qubit 0,
    # this is simply "Z". We use SparsePauliOp for this.
    observable = SparsePauliOp("Z")

    # Use the Estimator primitive to run the circuit.
    estimator = EstimatorV2(backend)
    
    # Execute the job. The Estimator expects a list of pairs, where each pair
    # is a (circuit, observable).
    job_hw = estimator.run([(qc, observable)])
    print(f"Job ID: {job_hw.job_id()}")
    print("Job sent to the backend. Waiting for results...")

    # Get the results from the job.
    result_hw = job_hw.result()
    
    # The result from an Estimator is an array of expectation values (evs).
    # Since we sent one job, we get the first value from the first result.
    # For state |1>, the expectation value of Z is -1.
    # Due to noise, the result will be close to -1.
    exp_val = result_hw[0].data.evs

    print(f"\nHardware Result (Expectation Value): {exp_val}")
    print("For an ideal X-gate, the state is |1>, and the expected Z value is -1.")


except Exception as e:
    print("\nCould not connect to IBM Quantum hardware.")
    print("Please ensure you have an IBM Quantum account and have saved your API token.")
    print("You can save your token using: QiskitRuntimeService.save_account(channel='ibm_quantum', token='YOUR_API_TOKEN')")
    print(f"Error details: {e}")


