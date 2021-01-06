from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities

import regex


def tohex(val, nbits):
    # https://stackoverflow.com/questions/7822956/how-to-convert-negative-integer-value-to-hex-in-python
    return hex((val + (1 << nbits)) % (1 << nbits))


def convert_str_to_int(num_str: str):
    num_str = num_str.strip()
    try:
        # Bitwise Complement (with all bits inversed): ~0b 1000 0000 0000 0000, i.e., 0b 0111 1111 1111 1111
        bitwise_complement = False
        if num_str.startswith('~'):
            bitwise_complement = True
            num_str = num_str.lstrip('~')
        # In fact, the type of constant depends on the variable.
        # For example, if the variable is long, then const will be convert to long even if it is int.
        # Since cannot get the variable type, there may be some false positives.
        is_long = False
        if num_str.endswith(('L', 'l')):
            num_str = num_str[:-1]
            is_long = True
        int_val = int(num_str, 0)
        if bitwise_complement:
            int_val = ~int_val

        # Notice 'negative' hex numbers in Java are positive in Python
        # Now, int_val can be a negative number in python, we need to map it back to hex number for Java
        if int_val < 0:
            hex_str = tohex(int_val, 64) if is_long else tohex(int_val, 32)
            int_val = int(hex_str, 0)

        return int_val
    except ValueError:
        return None


class IncompatMaskDetector(Detector):
    def __init__(self):
        self.regexpSign = regex.compile(
            r'\(\s*([~-]?(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.-])++)\s*([&|])\s*([~-]?(?:(?&aux1)|[\w.])++)\s*\)\s*([><=!]+)\s*([0-9a-zA-Z]+)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if not any(bitop in linecontent for bitop in ('&', '|')) and \
                not any(op in linecontent for op in ('>', '<', '>=', '<=', '==', '!=')):
            return

        its = self.regexpSign.finditer(linecontent.strip())
        for m in its:
            g = m.groups()
            operand_1 = g[0]
            bitop = g[2]
            operand_2 = g[3]
            relation_op = g[4]
            tgt_const_str = g[5]

            tgt_const = convert_str_to_int(tgt_const_str)
            if tgt_const is None:
                return

            op1 = convert_str_to_int(operand_1)
            op2 = convert_str_to_int(operand_2)

            if op1 is None and op2 is None:
                return

            if op1:
                const = op1
                const_str = operand_1
            else:
                const = op2
                const_str = operand_2
            is_long = True if const_str.endswith(('L', 'l')) else False

            priority = priorities.HIGH_PRIORITY
            p_type, description = None, None

            if relation_op in ('>', '<', '>=', '<=') and tgt_const == 0:
                if is_long:
                    max_positive = 0x7fffffffffffffff  # 9223372036854775807
                    min_negative = 0x8000000000000000  # -9223372036854775808
                    max_negative = 0xffffffffffffffff  # -1
                else:
                    max_positive = 0x7fffffff  # 2147483647
                    min_negative = 0x80000000  # -2147483648
                    max_negative = 0xffffffff  # -1

                if min_negative <= const <= max_negative:
                    p_type = 'BIT_SIGNED_CHECK_HIGH_BIT'
                    description = 'Check for sign of bitwise operation involving negative number.'
                    if relation_op in ('<', '>='):
                        priority = priorities.MEDIUM_PRIORITY
                elif 0 <= const <= max_positive:
                    p_type = 'BIT_SIGNED_CHECK'
                    description = 'Check for sign of bitwise operation.'
                    # at most 12 bits: -4096 <= const <= -1 or 0 <= const <= 4095
                    only_low_bits = const <= 0xfff
                    priority = priorities.LOW_PRIORITY if only_low_bits else priorities.MEDIUM_PRIORITY

            elif relation_op in ('==', '!='):
                priority = priorities.HIGH_PRIORITY
                p_type, description = None, None
                if const == 0:
                    p_type = 'BIT_AND_ZZ'
                    description = 'The expression of the form (e & 0) to 0 will always compare equal.'

            if p_type is not None:
                # get exact lineno
                get_exact_lineno = kwargs.get('get_exact_lineno', None)
                if get_exact_lineno:
                    tmp = get_exact_lineno(const_str)
                    if tmp:
                        lineno = tmp[1]

                self.bug_accumulator.append(BugInstance(p_type, priority, filename, lineno, description))




# Incompatible bit masks in yields a constant result (BIT_AND, BIT_IOR)