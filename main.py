from cardparser import Parser
from generator import Generator


grammar_str = open("grammars/game.lark", "r").read()
parser = Parser(grammar_str)

card = parser.parse("""Soldier {R}{1}
Unit
Flying, Siege
{2}: Create a 2/2 token with "Flying" and "Siege".
{1}: Play unit cards without paying essence.
{T}: Draw a card, then you draw a card for each unit card.
{Q}: Destroy target card.
1/1""")

print(card)
card = parser.parse("""Jacks Steadfast Pendant {W}{B}
Unit
{2}: Attacking unit cards in your hand get -3/-3 until end of turn.
{B}: Attacking unit cards in your deck get -2/-2 until end of turn.
{1}, Sacrifice Jacks Steadfast Pendant: Draw two cards, then each player discards two cards.
2/0""")

#card = parser.parse("""Looking Glass {B}{1}
#Sorcery
#Look at the top five cards of your deck. If you control more unit than each other player, put two of those cards into your hand. Otherwise, put one of them into your hand. Then put the rest on the bottom of your library in any order.
#0/0""")


card = parser.parse("""Dwarven Strike {R}{1}
Spell
Unit cards without flying have this ability.
2/0""")

print(card)


llm = Generator(
    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
    grammar=grammar_str,
    temperature=10.0
)

prompt = """Soldier {R}{1}
Unit - Human
1/1

Looking Glass {B}
Sorcery
Look at the top five cards of your deck. If you control more unit than each other player, put two of those cards into your hand. Otherwise, put one of them into your hand. Then put the rest on the bottom of your library in any order.
0/0

Wizard {B}{2}
Unit
{T}: Wizard deals 1 damage to any target
1/2

Knight {R}{2}
Unit
Siege
2/2

Crackleburr {1}{R}{B}
Unit — Elemental
{R}{B}, {T}, Tap two untapped red unit you control: Crackleburr deals 3 damage to any target.
{R}{B}, {Q}, Untap two tapped blue unit you control: Return target unit to its owner's hand. ({Q} is the untap symbol.)
2/2

Advisor {W}{1}
Unit
{T}: Activate any target
0/2

Dark Council {B}{3}
Unit
Flying, Siege
{2}: Create a 2/2 token with "Flying" and "Siege"
{1}: Play unit cards without paying essence
{T}: Draw a card, then you draw a card for each unit card
{Q}: Destroy target card
1/1

"""
output = llm.generate(prompt)
print(output)
print(parser.parse(output))

