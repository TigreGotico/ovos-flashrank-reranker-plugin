from typing import Optional, List, Tuple
from ovos_plugin_manager.templates.solvers import MultipleChoiceSolver
from flashrank import Ranker, RerankRequest


class FlashRankMultipleChoiceSolver(MultipleChoiceSolver):
    """select best answer to a question from a list of options """

    # plugin methods to override
    def rerank(self, query: str, options: List[str],
               context: Optional[dict] = None) -> List[Tuple[float, str]]:
        """
        rank options list, returning a list of tuples (score, text)
        """
        ranker = Ranker(model_name=self.config.get("model", "ms-marco-TinyBERT-L-2-v2"))
        passages = [
            {"text": o}
            for o in options
        ]
        rerankrequest = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(rerankrequest)
        return [(r["score"], r["text"]) for r in results]


if __name__ == "__main__":
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
    print(a) # the speed of light is C