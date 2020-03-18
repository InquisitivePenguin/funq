from transpiler import OpenQASMProgram, OpenQASMGate

class Output:
    program_header = """// Generated by the Funq compiler
OPENQASM 2.0;
include "qelib1.inc";
"""

    @staticmethod
    def generate_output(programs: dict, gates: dict):
        files = []
        for name in programs.keys():
            program = programs[name]
            comment_header = "// Program: " + name + ", " + str(program.qubits) + " qubits\n" + Output.program_header
            for n in gates.keys():
                gate = gates[n]
                comment_header += gate.emit() +"\n"
            program = comment_header + program.emit()
            files.append(program)
        return files
