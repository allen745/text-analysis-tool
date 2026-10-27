"""Shared test helper: a console that replays scripted answers.

``ScriptedConsole`` stands in for input()/print().  Each call to ``ask`` pops
the next scripted answer and records the prompt *and* the answer in the
transcript, so the transcript reads exactly like a real terminal session.
When the script runs out it raises EOFError, which is what a closed terminal
does, letting tests prove the program exits cleanly.
"""

from typing import List


class ScriptedConsole:
    def __init__(self, answers: List[str]) -> None:
        self._answers = list(answers)
        self.lines: List[str] = []          # everything shown on screen

    def ask(self, prompt: str) -> str:
        if not self._answers:
            raise EOFError
        answer = self._answers.pop(0)
        self.lines.append("%s%s" % (prompt, answer))
        return answer

    def show(self, message: str) -> None:
        self.lines.append(message)

    @property
    def transcript(self) -> str:
        return "\n".join(self.lines)

    def count_menus(self) -> int:
        """How many times the menu was displayed."""
        return self.transcript.count("==== Word and Text Analysis Tool ====")
