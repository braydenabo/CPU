HEADER = 'v3.0 hex words addressed'

INSTRUCTION_SET = {
    "ADD": {"opcode": "1100000", "type": "R"},  # ADD Rd, Rn, Rm
    "ADD_I": {"opcode": "0101000", "type": "I"},  # ADD Rd, Rn, imm5
    "SUB": {"opcode": "1110000", "type": "R"},  # SUB Rd, Rn, Rm
    "SUB_I": {"opcode": "0111000", "type": "I"},  # SUB Rd, Rn, imm5
    "LDR": {"opcode": "1100011", "type": "R"},  # LDR Rt, [Rn, Rm]
    "LDR_I": {"opcode": "0101011", "type": "I"},  # LDR Rt, [Rn, imm5]
    "STR": {"opcode": "1000100", "type": "R"},  # STR Rt, [Rn, Rm]
    "STR_I": {"opcode": "0001100", "type": "I"},  # STR Rt, [Rn, imm5]
}

REGISTER_MAP = {
    "X0": "00",
    "X1": "01",
    "X2": "10",
    "X3": "11",
}

def bin_to_hex(binary):
    """Convert binary string to hexadecimal."""
    return format(int(binary, 2), '04x')

def create_add_label(address):
    """Generate address label for hex output."""
    label = format(address, '08x')
    return f"{label[:2]}:"

def translate_instruction(line):
    """Translate an assembly instruction to binary machine code."""
    line = line.strip().replace(",", "").replace("[", "").replace("]", "")
    parts = line.split()
    instr = parts[0]

    # Check if the instruction exists in the set
    is_immediate = parts[-1].isdigit()  # Last operand is a number
    instr_key = f"{instr}_I" if is_immediate else instr

    if instr_key not in INSTRUCTION_SET:
        raise ValueError(f"Unknown instruction: {instr}")

    details = INSTRUCTION_SET[instr_key]
    opcode = details["opcode"]

    if details["type"] == "R":  # R-format (3 registers)
        if len(parts) != 4:
            raise ValueError(f"R-format instruction requires 3 registers: {line}")
        rd, rn, rm = parts[1], parts[2], parts[3]
        if rd not in REGISTER_MAP or rn not in REGISTER_MAP or rm not in REGISTER_MAP:
            raise ValueError(f"Invalid register in instruction: {line}")
        rd_bin = REGISTER_MAP[rd]
        rn_bin = REGISTER_MAP[rn]
        rm_bin = REGISTER_MAP[rm]
        return f"{opcode}{rm_bin}{'000'}{rn_bin}{rd_bin}"
    elif details["type"] == "I":  # I-format (2 registers + immediate)
        if len(parts) != 4:
            raise ValueError(f"I-format instruction requires 2 registers and an immediate: {line}")
        rt, rn, imm = parts[1], parts[2], parts[3]
        if rt not in REGISTER_MAP or rn not in REGISTER_MAP:
            raise ValueError(f"Invalid register in instruction: {line}")
        if not imm.isdigit():
            raise ValueError(f"Immediate value must be a number: {line}")
        rt_bin = REGISTER_MAP[rt]
        rn_bin = REGISTER_MAP[rn]
        imm_bin = format(int(imm), "05b")
        return f"{opcode}{imm_bin}{rn_bin}{rt_bin}"
    else:
        raise ValueError(f"Unsupported instruction type: {details['type']}")


def assemble(input_file, output_file):
    """Assemble assembly code into machine code."""
    
    memory = ["0000"] * 256
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        outfile.write(f"{HEADER}\n")

        address = 0  # Address counter
        for line in infile:
            if not line.strip() or line.startswith("#"):  # Skip blank/comment lines
                continue

            binary_code = translate_instruction(line)
            hex_code = bin_to_hex(binary_code)

            if address >= len(memory):
                raise ValueError("Program exceeds memory size (256 words).")

            memory[address] = hex_code
            address += 1

    # Write formatted output to the file
    with open(output_file, "w") as outfile:
        outfile.write(f"{HEADER}\n")

        # Format memory into 16 words per line with addressed output
        for i in range(0, len(memory), 16):
            address_label = format(i, '02x') + ":"
            line_data = " ".join(memory[i:i + 16])
            outfile.write(f"{address_label} {line_data}\n")

    print(f"Assembly complete. Output written to {output_file}")



if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python assembler.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        assemble(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
