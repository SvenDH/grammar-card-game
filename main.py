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
    EffectTransformer,
    CardTransformer
)
#from generator import Generator


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


def main():
    for card in cards:
        print(card.name)
        try:
            card.to_godot(f"project/cards/{card.name}.tres")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    typer.run(main)