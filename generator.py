from llama_cpp import Llama, LlamaGrammar

from models import TypeEnum, KeywordEnum
from cardparser import Parser


class Generator:
    def __init__(self, model_path: str, temperature: float = 1.0, debug: bool = True) -> None:
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
        self.parser = Parser(debug=debug)
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
