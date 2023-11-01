import typer
import asyncio

from parse import (
    Parser,
    DropLetters,
    NumberTransformer,
    OperatorTransformer,
    BaseTransformer,
    KeywordTransformer,
    ReferenceTransformer,
    ObjectTransformer,
    EffectTransformer,
    CardTransformer
)
#from generator import Generator
from game import Game, CallbackManager


parser = Parser([
    DropLetters(),
    NumberTransformer(),
    OperatorTransformer(),
    BaseTransformer(),
    KeywordTransformer(),
    ReferenceTransformer(),
    ObjectTransformer(),
    EffectTransformer(),
    CardTransformer()
])
text = open("cards/cards.txt").read().strip()

cards = []
for t in text.split("\n\n"):
    card = parser.parse(t)
    cards.append(card)

"""
llm = Generator(
    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
    temperature=10.0
)
output = llm.generate(text + "\n\n")
print(output)
print(parser.parse(output))
"""


class CliManager(CallbackManager):
    def confirm(self, msg: str) -> bool:
        return typer.confirm("\n" + msg + "\nConfirm?")

    def choose(self, msg: str, options: list) -> int:
        typer.echo("\n" + msg + "\n" + "".join([f"[{i+1}]: {o}\n" for i, o in enumerate(options)]))
        while True:
            index = int(typer.prompt(f"Choose one option [1-{len(options)}]")) - 1
            if 0 <= index < len(options):
                return index

    def order(self, msg: str, options: list) -> list:
        assert len(options) > 0
        typer.echo("\n" + msg + "\n" + "".join([f"[{i+1}]: {o}\n" for i, o in enumerate(options)]))
        ordered = []
        result = typer.prompt(f"Choose order from resolving first to last [1-{len(options)}] or press 's' to keep order of remaining options")
        while result != "s":
            index = int(result) - 1
            if index in ordered:
                ordered.remove(index)
            if index in options:
                options.remove(index)
            ordered.append(index)
            result = typer.prompt("[" + ", ".join(ordered) + "] Next option:")
        
        return ordered + options


def main():
    game = Game()
    player1 = game.add_player("player_1", cards)
    player2 = game.add_player("player_2", cards)
    player1.callback = CliManager()

    asyncio.run(game.start())


if __name__ == "__main__":
    typer.run(main)