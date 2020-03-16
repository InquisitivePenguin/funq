

class Types:
    classical_types = ["Const", "C[]"]
    quantum_types = ["Q", "Q[]"]

    @staticmethod
    def is_classical(typename):
        return typename in Types.classical_types

    @staticmethod
    def is_quantum(typename):
        return typename in Types.quantum_types

    @staticmethod
    def is_valid(typename):
        return Types.is_valid(typename) or Types.is_quantum(typename)
