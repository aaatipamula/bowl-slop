import sys
from typing import Dict, Iterable, List, Tuple

PDAMap = Dict[Tuple[str, str], Tuple[str, str, str]]
CheckReturn = Tuple[bool, List[Tuple[str, str, str]]]

class Stack(list):
    def __init__(self) -> None:
        self.push = self.append

    def pops(self, expect: str):
        if self.pop() != expect:
            raise RuntimeError("Invalid stack symbol removed")

class PDA:
    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        start_state: str,
        final_states: List[str]
    ) -> None:
        self.states = states
        self.alphabet = alphabet
        self.start_state = start_state
        self.final_states = final_states

        self.map: PDAMap = {}

    @classmethod
    def from_file(cls, file: str):
        with open(file, "r") as f:
            states = f.readline().strip().split()
            alphabet = f.readline().strip().split()
            start_state = f.readline().strip()
            final_states = f.readline().strip().split()
            pda = cls(states, alphabet, start_state, final_states)

            map = {}
            try:
                for line in f:
                    if line in ("\n", ""): continue
                    f, r, pop, push, t = line.strip().split()
                    map[(f, r)] = (pop, push, t)
            except ValueError:
                print("Invalid file format")
                exit(1)

            pda.map = map

        return pda

    def check(self, input: str, *, debug: bool = False) -> CheckReturn:
        stack = Stack()
        curr_state = self.start_state
        characters = input.strip().split()
        traceback = []

        while len(characters) > 0 and curr_state not in self.final_states:
            character = characters.pop(0)

            if character not in self.alphabet:
                return False, traceback
            
            next = self.map.get((curr_state, character))
            if next is None:
                next = self.map.get((curr_state, "lambda"))
                characters.insert(0, character)
                if next is None:
                    return False, traceback

            pop, push, next_state = next # Unpack values
            
            try:
                if pop != "lambda": stack.pops(pop)
                if push != "lambda": stack.push(push)
            except Exception:
                return False, traceback

            if debug: print((curr_state, character, next_state), stack, characters)
            traceback.append((curr_state, character, next_state))

            curr_state = next_state

        while self.map.get((curr_state, "lambda")) and curr_state not in self.final_states:
            next = self.map.get((curr_state, "lambda"))
            if next is None:
                return False, traceback

            pop, push, next_state = next # Unpack values
            
            try:
                if pop != "lambda": stack.pops(pop)
                if push != "lambda": stack.push(push)
            except Exception:
                return False, traceback

            if debug: print((curr_state, "lambda", next_state), stack, characters)
            traceback.append((curr_state, "lambda", next_state))

            curr_state = next_state

        while len(characters) > 0:
            character = characters.pop(0)

            if character not in self.alphabet:
                return False, traceback
            
            next = self.map.get((curr_state, character))
            if next is None:
                characters.insert(0, character)
                break

            pop, push, next_state = next # Unpack values
            
            try:
                if pop != "lambda": stack.pops(pop)
                if push != "lambda": stack.push(push)
            except Exception:
                return False, traceback

            if debug: print((curr_state, character, next_state), stack, characters)
            traceback.append((curr_state, character, next_state))

        accepted = len(stack) == 0 \
            and curr_state in self.final_states \
            and len(characters) == 0

        return accepted, traceback

def printl(o: Iterable):
    for v in o:
        print(v)

def test():
    pda = PDA.from_file("./data.txt")
    tests = [
        ("bowl", True),
        ("bowl bowl", False),
        ("bowl chicken", True),
        ("bowl chicken chicken", False),
        ("bowl rice chicken", True),
        ("bowl rice chicken lettuce beans white", True),
        ("bowl noodle beef marinara", True),
        ("sandwich", False),
        ("sandwich bun", True),
        ("sandwich beef", False),
        ("sandwich bread beef", True),
        ("sandwich bread turkey mayonnaise cheese", True),
        ("sandwich sub toasted beef onions cheese", True),
        ("wrap", False),
        ("wrap tortilla", True),
        ("wrap lamb", False),
        ("wrap pita lamb", True),
        ("wrap tortilla chicken", True),
        ("wrap tortilla beef lettuce cheese hot avocado", True),
    ]

    for test, expected in tests:
        accepted, _ = pda.check(test)
        try:
            assert accepted == expected
        except AssertionError:
            print(f"Expected ({expected}) got ({accepted}) for:\n{test}\n")

def main():
    pda = PDA.from_file("./data.txt")

    debug = False
    if len(sys.argv) > 1:
        debug = sys.argv[1].lower() == "debug"

    while True:
        user_string = input("> ")
        if user_string.lower() == "exit": break
        accepted, traceback = pda.check(user_string, debug=debug)
        if accepted:
            print("accepted")
            printl(traceback)
        else:
            print("rejected")

if __name__ == "__main__":
    test()
    main()

