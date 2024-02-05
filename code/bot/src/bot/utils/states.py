from enum import Enum
from collections import namedtuple

Stage = namedtuple('Stage', ('Level, Branch ,Step'))

class State(Enum):
    START =     Stage(0,0,0)
    FILM =      Stage(1,1,0)
    OV =        Stage(1,1,1)
    IMAX =      Stage(1,1,2)
    _3d =       Stage(1,1,3)
    DATE =      Stage(1,1,4)
    TIME =      Stage(1,1,5)
    BUY =       Stage(1,1,6)
    OUTCOMING = Stage(1,2,0)
    BOOK =      Stage(1,2,1)

    def go_back(self) -> 'State':
        """Return the previous state."""

        # If the current state is the start or the first step of a branch, return to State.START
        if self == State.START or self.value.Step - 1 < self._min_step_for_branch():
            return State.START
        return State(Stage(self.value.Level, self.value.Branch, self.value.Step - 1))

    def _min_step_for_branch(self) -> int:
        """Return the minimum step for the current branch."""
        return min(state.value.Step for state
                    in
                    {state for state in State if state.value.Branch == self.value.Branch}
                )
