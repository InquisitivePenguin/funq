from visitor import Visitor
from scope import Scope
from standard_library import StandardLibrary
from qasm import *


# A Transpiler converts an AST into OpenQASM programs by visiting the nodes
# and converting.
class Transpiler:
    def __init__(self, state):
        self.regions = state.regions
        self.functions = state.functions
        self.programs = {}
        self.gates = {}

    def transpile(self):
        for name in self.functions.keys():
            f = self.functions[name]
            self.generate_gate(name, f[0], f[1], f[2])
        for name in self.regions.items():
            r = self.regions[name]
            self.generate_program(name, r[0], r[1])

    def visit_region(self, region):
        print("Visiting region")
        name = region.get_name().name
        instructions = self.convert_to_instructions(region.get_block())
        print(instructions)
        self.regions[name] = instructions

    def generate_gate(self, func_name, cargs, qargs, block):
        instructions = self.convert_to_instructions(block)
        self.gates[func_name] = OpenQASMGate(func_name, cargs, qargs, instructions)

    def generate_program(self, name, qubits, block):
        instructions = self.convert_to_instructions(block)
        self.programs[name] = OpenQASMProgram(qubits, instructions)

    def convert_to_instructions(self, stmt: Scope) -> list:
        if stmt.data == "block":
            return [self.convert_to_instructions(s) for s in stmt.children]
        elif stmt.data == "function_call":
            cargs = stmt.get_call_list().get_classical_arguments()
            qargs = stmt.get_call_list().get_quantum_arguments()
            # Is this in the standard library?
            if StandardLibrary.is_standard(stmt.get_name().name):
                return [FunctionCall(StandardLibrary.get_standard_name(stmt.get_name().name), cargs, qargs)]
            else:
                return [FunctionCall(stmt.get_name().name, cargs, qargs)]
        elif stmt.data == "if":
            arg1, arg2 = stmt.get_args()
            op = stmt.get_op()
            arg1 = self.convert_classical_arg(arg1)
            arg2 = self.convert_classical_arg(arg2)
            comp = Comparison(arg1, arg2, op)
            sub_instructions = [self.convert_to_instructions(c) for c in stmt.get_block().children]
            return [IfInstruction(comp, sub_instructions)]
        elif stmt.data == "q_decl":
            name = stmt.get_name().name
            size = stmt.get_length()
            return [QuantumInitialization(name, size)]
        elif stmt.data == "c_decl":
            name = stmt.get_name().name
            size = stmt.get_length()
            return [ClassicalInitialization(name, size)]
        elif stmt.data == "measurement":
            raise Exception("Unimplemented")
        else:
            raise Exception("Unexpected statement type: " + str(stmt.__dict__))

    def convert_classical_arg(self, arg):
        if arg.type == "uint":
            return UIntArgument(arg.value)
        elif arg.type == "v_ident":
            return CRegArgument(arg.name)
        else:
            raise Exception("Unexpected argument type!")


class OpenQASMProgram:
    def __init__(self, qubits, instructions):
        self.qubits = qubits
        self.instructions = instructions

    def add_instruction(self, instructions):
        self.instructions += instructions

    def emit(self):
        emission = ""
        for instruction in self.instructions:
            emission += instruction.emit()
        return emission


class OpenQASMGate:
    def __init__(self, name, cargs, qargs, instructions):
        self.instructions = instructions
        self.name = name
        self.cargs = cargs
        self.qargs = qargs

    def add_instruction(self, instructions):
        self.instructions += instructions

    def emit(self):
        header = "gate " + self.name + " (" + ",".join(self.cargs) + ") " + ",".join(self.qargs) + "{\n"
        body = "".join([instruction.emit() for instruction in self.instructions])
        tail = "\n}"
        return header + body + tail
