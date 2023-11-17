import typer

from parse import (
    Parser,
    DropLetters,
    NumberTransformer,
    OperatorTransformer,
    BaseTransformer,
    KeywordTransformer,
    ReferenceTransformer,
    ObjectTransformer,
    CardTransformer
)

#from generator import Generator

"""
llm = Generator(
    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
    temperature=10.0
)
output = llm.generate(text + "\n\n")
print(output)
print(parser.parse(output))
"""


def main(path: str = "cards/cards.txt"):
    parser = Parser([
        DropLetters(),
        NumberTransformer(),
        OperatorTransformer(),
        BaseTransformer(),
        KeywordTransformer(),
        ReferenceTransformer(),
        ObjectTransformer(),
        CardTransformer()
    ])

    cards = []
    for t in open(path).read().strip().split("\n\n"):
        card = parser.parse(t)
        cards.append(card)
    for card in cards:
        try:
            card.to_godot(f"project/cards/{card.name}.tres")
        except:
            print(f"{card.name} failed")

if __name__ == "__main__":
    typer.run(main)