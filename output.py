class Output:
    program_header = """
    // Generated by the Funq compiler
    OPENQASM 2.0;
    include "qelib1.inc"
    """

    # Note: each region is a list of instructions
    def __init__(self, regions):
        self.regions = regions

    def generate_output(self):
        files = []
        for region in self.regions:
            comment_header = "// Program: " + region[0] + ", " + str(region[1]) + " qubits\n"
            program = comment_header + Output.program_header
            for instruction in region:
                program += instruction.emit() + "\n"
            files.append(program)
        return files
