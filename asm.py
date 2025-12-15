import sys
import argparse
import csv
from pathlib import Path

# ------------------ ОПЕРАЦИИ ------------------
OPCODES = {
    'LOAD': 13,
    'READ': 0,
    'WRITE': 8,
    'ADD': 1,
}

def encode_load(reg: int, const: int) -> bytes:
    # A(4) | B(7) | C(22)
    word = (OPCODES['LOAD'] & 0xF) | ((reg & 0x7F) << 4) | ((const & 0x3FFFFF) << 11)
    return word.to_bytes(6, 'little')

def encode_read(offset: int, addr_reg: int, dst_reg: int) -> bytes:
    # A(4) | B(7) | C(7) | D(7)
    word = (OPCODES['READ'] & 0xF) \
           | ((offset & 0x7F) << 4) \
           | ((addr_reg & 0x7F) << 11) \
           | ((dst_reg & 0x7F) << 18)
    return word.to_bytes(6, 'little')

def encode_write(src_reg: int, mem_addr: int) -> bytes:
    # A(4) | B(7) | C(17)
    word = (OPCODES['WRITE'] & 0xF) | ((src_reg & 0x7F) << 4) | ((mem_addr & 0x1FFFF) << 11)
    return word.to_bytes(6, 'little')

def encode_add(dst_reg: int, addr1: int, addr2: int) -> bytes:
    # A(4) | B(7) | C(17) | D(17)
    word = (OPCODES['ADD'] & 0xF) \
           | ((dst_reg & 0x7F) << 4) \
           | ((addr1 & 0x1FFFF) << 11) \
           | ((addr2 & 0x1FFFF) << 28)
    return word.to_bytes(6, 'little')

def parse_and_assemble(input_file: Path):
    instructions = []
    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            op = row[0].strip().upper()
            args = [int(x.strip()) for x in row[1:]]
            if op == 'LOAD':
                reg, const = args
                code = encode_load(reg, const)
                instructions.append(('LOAD', reg, const, code))
            elif op == 'READ':
                offset, addr_reg, dst_reg = args
                code = encode_read(offset, addr_reg, dst_reg)
                instructions.append(('READ', offset, addr_reg, dst_reg, code))
            elif op == 'WRITE':
                src_reg, mem_addr = args
                code = encode_write(src_reg, mem_addr)
                instructions.append(('WRITE', src_reg, mem_addr, code))
            elif op == 'ADD':
                dst_reg, addr1, addr2 = args
                code = encode_add(dst_reg, addr1, addr2)
                instructions.append(('ADD', dst_reg, addr1, addr2, code))
            else:
                raise ValueError(f"Unknown operation: {op}")
    return instructions

def main():
    parser = argparse.ArgumentParser(description='Ассемблер для УВМ (Вариант 2)')
    parser.add_argument('input', help='Путь к CSV-файлу с программой')
    parser.add_argument('-o', '--output', required=True, help='Путь к бинарному файлу результата')
    parser.add_argument('--test', action='store_true', help='Режим тестирования: вывод внутреннего представления и байткода')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Файл не найден: {input_path}", file=sys.stderr)
        sys.exit(1)

    instructions = parse_and_assemble(input_path)

    if args.test:
        for instr in instructions:
            op = instr[0]
            fields = instr[1:-1]
            bytecode = instr[-1]
            print(f"{op}: {fields} → {', '.join(f'0x{b:02X}' for b in bytecode)}")

    # Запись в бинарный файл
    with open(args.output, 'wb') as f:
        for instr in instructions:
            f.write(instr[-1])

    print(f"Размер двоичного файла: {len(instructions) * 6} байт", file=sys.stderr)

if __name__ == "__main__":
    main()