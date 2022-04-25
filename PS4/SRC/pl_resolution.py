import copy
import itertools
from typing import Union


class Literal:
    def __init__(self, string):
        sym = string.strip('-')
        if len(sym) != 1:
            raise ValueError
        self.symbol = sym
        self.neg = string.startswith('-')

    def is_negative(self):
        return self.neg

    def complement(self, other):
        return self.symbol == other.symbol and self.neg != other.neg

    def __str__(self):
        return ('-' if self.neg else '') + self.symbol

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.symbol == other.symbol and self.neg == other.neg

    def __lt__(self, other):
        if self.symbol == other.symbol:
            return int(self.neg) < int(other.neg)
        return self.symbol < other.symbol

    def __hash__(self) -> int:
        return hash((self.symbol, self.neg))


class Clause:
    def __init__(self, list_of_literals):
        self.literals = list_of_literals
        self._factor()

    @classmethod
    def fromstring(cls, string):
        lits = [] if string == '' else string.split(' OR ')
        lits = [Literal(lit) for lit in lits]
        return cls(lits)

    def is_empty(self):
        return len(self.literals) == 0

    def is_EquivalentToTrue(self):
        i = 0
        while i < len(self) - 1:
            if self.literals[i].complement(self.literals[i + 1]):
                return True
            i += 1
        return False

    def symbols(self):
        return set(x.symbol for x in self.literals)

    def _factor(self):
        self.literals = list(set(self.literals))
        self.literals.sort()

    def __str__(self):
        if self.is_empty():
            return r'{}'
        return ' OR '.join([str(lit) for lit in self.literals])

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.literals == other.literals

    def __hash__(self):
        return hash(tuple(self.literals))

    def __len__(self):
        return len(self.literals)


def nega(term: Union[Literal, Clause]):
    if type(term) == Literal:
        return Literal(('' if term.is_negative() else '-') + term.symbol)
    return [Clause([nega(lit)]) for lit in term.literals]


def resolve(clause1, clause2):
    lits = clause1.literals + clause2.literals
    lits = sorted(list(set(lits)))

    i = 0
    is_complementPair = False
    while i < len(lits) - 1:
        if lits[i].complement(lits[i + 1]):
            is_complementPair = True
            lits.pop(i)
            lits.pop(i)
            break
        i += 1

    return Clause(lits) if is_complementPair else None


def pl_resolution(kb, alpha, result_buffer) -> bool:
    clauses = kb + nega(alpha)
    new = []

    i = 0
    while True:
        newResolvents = []
        for x, y in itertools.product(clauses, repeat=2):
            resolvent = resolve(x, y)

            if resolvent is None:
                continue

            if resolvent not in new and \
               resolvent not in newResolvents and \
               resolvent not in clauses and \
               not resolvent.is_EquivalentToTrue():
                newResolvents.append(resolvent)

        result_buffer.append((len(newResolvents), copy.copy(newResolvents)))

        if Clause([]) in newResolvents:
            result_buffer.append('YES')
            return True

        new.extend(newResolvents)

        if set(new).issubset(set(clauses)):
            result_buffer.append('NO')
            return False

        clauses = list(set(clauses).union(new))
        i += 1


if __name__ == '__main__':
    n = 5
    for i in range(n):
        with open(f'input/input{i+1}.txt') as input:
            alpha = input.readline().strip()
            num_clauses = int(input.readline().strip())

            clauses = []
            for _ in range(num_clauses):
                clauses.append(input.readline().strip())

            kb = [Clause.fromstring(x) for x in clauses]
            alpha = Clause.fromstring(alpha)
            write_buffer = []

            print(
                f'Test {i+1} result: {pl_resolution(kb, alpha, write_buffer)}')

        with open(f'output/output{i+1}.txt', mode='w+') as output:
            for elem in write_buffer:
                if type(elem) == tuple:
                    num_resolvents, resolvents = elem
                    output.write(str(num_resolvents) + '\n')
                    output.writelines([str(x) + '\n' for x in resolvents])
                else:
                    output.writelines([elem])
