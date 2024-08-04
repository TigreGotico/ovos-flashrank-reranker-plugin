from typing import Optional, List, Tuple, Dict, Iterable

from flashrank import Ranker, RerankRequest
from ovos_plugin_manager.templates.solvers import MultipleChoiceSolver, QuestionSolver, EvidenceSolver
from ovos_utils.log import LOG
from quebra_frases import sentence_tokenize


class FlashRankMultipleChoiceSolver(MultipleChoiceSolver):
    """select best answer to a question from a list of options """

    def __init__(self, config=None):
        config = config or {"min_conf": None,
                            "n_answer": 1,
                            "model": "ms-marco-MultiBERT-L-12"}
        super().__init__(config)

    # plugin methods to override
    def rerank(self, query: str, options: List[str], lang: Optional[str] = None) -> List[Tuple[float, str]]:
        """
        rank options list, returning a list of tuples (score, text)
        """
        ranker = Ranker(model_name=self.config.get("model", "ms-marco-MultiBERT-L-12"))
        passages = [
            {"text": o}
            for o in options
        ]
        rerankrequest = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(rerankrequest)
        return [(r["score"], r["text"]) for r in results]


class FlashRankEvidenceSolverPlugin(EvidenceSolver):
    """extract best sentence from text that answers the question, using flashrank"""

    def __init__(self, config=None):
        config = config or {"min_conf": None,
                            "n_answer": 1,
                            "model": "ms-marco-MultiBERT-L-12"}
        super().__init__(config)
        self.ranker = FlashRankMultipleChoiceSolver(self.config)

    def get_best_passage(self, evidence, question, context=None):
        """
        evidence and question assured to be in self.default_lang
         returns summary of provided document
        """
        sents = []
        for s in evidence.split("\n"):
            sents += sentence_tokenize(s)
        sents = [s.strip() for s in sents if s]
        return self.ranker.select_answer(question, sents, context)


class FlashRankCorpusSolver(QuestionSolver):
    enable_tx = False
    priority = 60

    def __init__(self, config=None):
        config = config or {"min_conf": None,
                            "n_answer": 1,
                            "model": "ms-marco-MultiBERT-L-12"}
        super().__init__(config)
        self.corpus = None
        self.ranker = FlashRankMultipleChoiceSolver(self.config)

    def load_corpus(self, corpus: List[str]):
        self.corpus = corpus

    def retrieve_from_corpus(self, query, k=3) -> Iterable[Tuple[float, str]]:
        yield from self.ranker.rerank(query, self.corpus)

    def get_spoken_answer(self, query: str, context: Optional[dict] = None) -> str:
        if self.corpus is None:
            return None
        # Query the corpus
        answers = [a[1] for a in self.retrieve_from_corpus(query, k=self.config.get("n_answer", 1))]
        if answers:
            return ". ".join(answers[:self.config.get("n_answer", 1)])


class FlashRankQACorpusSolver(FlashRankCorpusSolver):
    def __init__(self, config=None):
        self.answers = {}
        super().__init__(config)

    def load_corpus(self, corpus: Dict):
        self.answers = corpus
        super().load_corpus(list(self.answers.keys()))

    def retrieve_from_corpus(self, query, k=1) -> Iterable[Tuple[float, str]]:
        for score, q in super().retrieve_from_corpus(query, k):
            LOG.debug(f"closest question in corpus: {q}")
            yield score, self.answers[q]


if __name__ == "__main__":
    LOG.set_level("DEBUG")
    p = FlashRankMultipleChoiceSolver()
    a = p.rerank("what is the speed of light", [
        "very fast", "10m/s", "the speed of light is C"
    ])
    print(a)
    # [(0.999819, 'the speed of light is C'),
    # (2.7686672e-05, 'very fast'),
    # (1.2555749e-05, '10m/s')]

    a = p.select_answer("what is the speed of light", [
        "very fast", "10m/s", "the speed of light is C"
    ])
    print(a)  # the speed of light is C

    config = {
        "lang": "en-us",
        "min_conf": 0.4,
        "n_answer": 1
    }
    solver = FlashRankEvidenceSolverPlugin(config)

    text = """Mars is the fourth planet from the Sun. It is a dusty, cold, desert world with a very thin atmosphere. 
Mars is also a dynamic planet with seasons, polar ice caps, canyons, extinct volcanoes, and evidence that it was even more active in the past.
Mars is one of the most explored bodies in our solar system, and it's the only planet where we've sent rovers to roam the alien landscape. 
NASA currently has two rovers (Curiosity and Perseverance), one lander (InSight), and one helicopter (Ingenuity) exploring the surface of Mars.
"""
    query = "how many rovers are currently exploring Mars"
    answer = solver.get_best_passage(evidence=text, question=query)
    print("Query:", query)
    print("Answer:", answer)
    # 2024-07-22 17:08:38.542 - OVOS - ovos_plugin_manager.language:create:233 - INFO - Loaded the Language Translation plugin ovos-translate-plugin-server
    # 2024-07-22 17:08:38.543 - OVOS - ovos_plugin_manager.utils.config:get_plugin_config:40 - DEBUG - Loaded configuration: {'module': 'ovos-translate-plugin-server', 'lang': 'en-us'}
    # 2024-07-22 17:08:38.552 - OVOS - ovos_plugin_manager.language:create:233 - INFO - Loaded the Language Translation plugin ovos-translate-plugin-server
    # 2024-07-22 17:08:38.552 - OVOS - ovos_plugin_manager.utils.config:get_plugin_config:40 - DEBUG - Loaded configuration: {'module': 'ovos-translate-plugin-server', 'lang': 'en-us'}
    # Query: how many rovers are currently exploring Mars
    # Answer: NASA currently has two rovers (Curiosity and Perseverance), one lander (InSight), and one helicopter (Ingenuity) exploring the surface of Mars.

    # Create your corpus here
    corpus = [
        "a cat is a feline and likes to purr",
        "a dog is the human's best friend and loves to play",
        "a bird is a beautiful animal that can fly",
        "a fish is a creature that lives in water and swims",
    ]

    s = FlashRankCorpusSolver({})
    s.load_corpus(corpus)

    query = "does the fish purr like a cat?"
    print(s.spoken_answer(query))

    # 2024-07-22 17:08:38.595 - OVOS - ovos_plugin_manager.language:create:233 - INFO - Loaded the Language Translation plugin ovos-translate-plugin-server
    # 2024-07-22 17:08:38.595 - OVOS - ovos_plugin_manager.utils.config:get_plugin_config:40 - DEBUG - Loaded configuration: {'module': 'ovos-translate-plugin-server', 'lang': 'en-us'}
    # 2024-07-22 17:08:38.605 - OVOS - ovos_plugin_manager.language:create:233 - INFO - Loaded the Language Translation plugin ovos-translate-plugin-server
    # 2024-07-22 17:08:38.605 - OVOS - ovos_plugin_manager.utils.config:get_plugin_config:40 - DEBUG - Loaded configuration: {'module': 'ovos-translate-plugin-server', 'lang': 'en-us'}
    # a cat is a feline and likes to purr