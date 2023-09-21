#from llama_cpp import Llama, LlamaGrammar

from cardparser import Parser


grammar_str = open("grammars/game.lark", "r").read()
parser = Parser(grammar_str)

card = parser.parse("""Soldier {R}{1}
Creature
Flying, Siege
{2}: Create a 2/2 token with "Flying" and "Siege".
{1}: Play creature cards without paying essence.
{T}: Draw a card, then you draw a card for each creature card.
{Q}: Destroy target card.
1/1""")

print(card)
card = parser.parse("""Jacks Steadfast Pendant {W}{B}
Creature
{2}: Attacking creature cards in your hand get -3/-3 until end of turn.
{B}: Attacking creature cards in your deck get -2/-2 until end of turn.
{1}, Sacrifice Jacks Steadfast Pendant: Draw two cards, then each player discards two cards.
2/0""")

#card = parser.parse("""Looking Glass {B}{1}
#Sorcery
#Look at the top five cards of your deck. If you control more creatures than each other player, put two of those cards into your hand. Otherwise, put one of them into your hand. Then put the rest on the bottom of your library in any order.
#0/0""")

print(card)

'''

class Generator:
    def __init__(self, model_path: str, grammar: str, temperature: float = 1.0, debug: bool = True) -> None:
        self.temperature = temperature
        self.model = Llama(
            model_path,
            seed=-1,
            n_ctx=512,
            n_gpu_layers=128,
            n_batch=512,
            f16_kv=True,
            logits_all=False,
            vocab_only=False,
            use_mlock=False,
        )
        self.parser = Parser(grammar, debug)
        self.name_grammar = LlamaGrammar.from_string(r'root ::= [A-Z][a-z]*(" " [A-Z][a-z]*)* " {"')

    def generate(self, prompt: str, name: str | None = None):
        if name is None:
            result = self.model(prompt=prompt, grammar=self.name_grammar, temperature=self.temperature)
            name = result["choices"][0]["text"].strip(" {")
        
        g = self.parser.grammar.format(
            name=f'"{name}"',
            types=TypeEnum.to_grammar(),
            keywords=KeywordEnum.to_grammar()
        )
        g = g.replace(" /", " ").replace("/ ", " ").replace("/\n", "\n").replace("\n|", " |").replace(": ", " ::= ")
        g = LlamaGrammar.from_string(g)
        result = self.model(
            prompt=prompt,
            grammar=g,
            temperature=self.temperature,
            max_tokens=256
        )
        return result["choices"][0]["text"]

llm = Generator(
    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
    grammar=grammar_str,
    temperature=10.0
)

prompt = """Soldier {R}{1}
Creature - Human
1/1

Looking Glass {B}
Sorcery
Look at the top five cards of your deck. If you control more creatures than each other player, put two of those cards into your hand. Otherwise, put one of them into your hand. Then put the rest on the bottom of your library in any order.
0/0

Wizard {B}{2}
Creature
{T}: Wizard deals 1 damage to any target
1/2

Knight {R}{2}
Creature
Siege
2/2

Crackleburr {1}{R}{B}
Creature — Elemental
{R}{B}, {T}, Tap two untapped red creatures you control: Crackleburr deals 3 damage to any target.
{R}{B}, {Q}, Untap two tapped blue creatures you control: Return target creature to its owner's hand. ({Q} is the untap symbol.)
2/2

Advisor {W}{1}
Creature
{T}: Activate any target
0/2

Dark Council {B}{3}
Creature
Flying, Siege
{2}: Create a 2/2 token with "Flying" and "Siege"
{1}: Play creature cards without paying essence
{T}: Draw a card, then you draw a card for each creature card
{Q}: Destroy target card
1/1

"""
output = llm.generate(prompt)
print(output)
print(parser.parse(output))

'''