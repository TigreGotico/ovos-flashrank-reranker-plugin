# FlashRankMultipleChoiceSolver for OVOS

The `FlashRankMultipleChoiceSolver` plugin is designed for the Open Voice OS (OVOS) platform to help select the best
answer to a question from a list of options. This plugin utilizes the FlashRank library to evaluate and rank
multiple-choice answers based on their relevance to the given query.

## Features

- **Rerank Options**: Reranks a list of options based on their relevance to the query.
- **Customizable Model**: Allows the use of different ranking models.
- **Seamless Integration**: Designed to work with OVOS plugin manager.

ReRanking is a technique used to refine a list of potential answers by evaluating their relevance to a given query.
This process is crucial in scenarios where multiple options or responses need to be assessed to determine the most
appropriate one.

In retrieval chatbots, ReRanking helps in selecting the best answer from a set of retrieved documents or options,
enhancing the accuracy of the response provided to the user.

## Configuration

`MultipleChoiceSolver` are integrated into the OVOS Common Query framework, where they are used to select the most
relevant answer from a set of multiple skill responses.

```json
"common_query": {
  "reranker": "ovos-flashrank-reranker-plugin",
  "ignore_skill_scores": true,
  "ovos-flashrank-reranker-plugin": {"model": "ms-marco-TinyBERT-L-2-v2"}
}
```

> NOTE: enabling this on a raspberry pi will introduce up to 1 second of extra latency in common query pipeline

### Available Models

Below is the list of models supported as of now, by default `ms-marco-MultiBERT-L-12` is used due to being multilingual:

| Model Name                                       | Description                                                                                                                                                                                                                                                                                                                                                                    |
|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ms-marco-TinyBERT-L-2-v2`             | [Model card](https://huggingface.co/cross-encoder/ms-marco-TinyBERT-L-2) Trained on the MS Marco Passage Ranking task. This model encodes queries and ranks passages retrieved from large-scale datasets like MS MARCO, focusing on machine reading comprehension and passage ranking.                                                                                         |
| `ms-marco-MiniLM-L-12-v2`                        | [Model card](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2) Trained on MS MARCO Passage Ranking, it performs well for Information Retrieval tasks, encoding queries and sorting passages. It offers high performance with a lower documents per second rate compared to other versions.                                                                         |
| `ms-marco-MultiBERT-L-12` (default)                        | Multi-lingual, [supports 100+ languages](https://github.com/google-research/bert/blob/master/multilingual.md#list-of-languages)                                                                                                                                                                                                                                                |
| `ce-esci-MiniLM-L12-v2`                          | [FT on Amazon ESCI dataset](https://github.com/amazon-science/esci-data) Fine-tuned on the Amazon ESCI dataset, which includes queries in English, Japanese, and Spanish. Designed for semantic search and ranking, this model maps sentences and paragraphs to a 384-dimensional vector space, useful for tasks like clustering and product search in a multilingual context. |
| `rank-T5-flan` | [Model card](https://huggingface.co/bergum/rank-T5-flan) Best non cross-encoder reranker                                                                                                                                                                                                                                                                                                                       |
| `rank_zephyr_7b_v1_full` (4-bit-quantised GGUF)  | A 7B parameter GPT-like model fine-tuned on task-specific listwise reranking data. It is the state-of-the-art open-source reranking model for several datasets                                                                                                                                                                                                                 |

## Standalone Usage

#### FlashRankMultipleChoiceSolver

FlashRankMultipleChoiceSolver is designed to select the best answer to a question from a list of options.

In the context of retrieval chatbots, FlashRankMultipleChoiceSolver is useful for scenarios where a user query results
in a list of predefined answers or options.
The solver ranks these options based on their relevance to the query and selects the most suitable one.

```python
from ovos_flashrank_solver import FlashRankMultipleChoiceSolver

solver = FlashRankMultipleChoiceSolver()
a = solver.rerank("what is the speed of light", [
    "very fast", "10m/s", "the speed of light is C"
])
print(a)
# 2024-07-22 15:03:10.295 - OVOS - __main__:load_corpus:61 - DEBUG - indexed 3 documents
# 2024-07-22 15:03:10.297 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 1 (score: 0.7198746800422668): the speed of light is C
# 2024-07-22 15:03:10.297 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 2 (score: 0.0): 10m/s
# 2024-07-22 15:03:10.297 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 3 (score: 0.0): very fast
# [(0.7198747, 'the speed of light is C'), (0.0, '10m/s'), (0.0, 'very fast')]

# NOTE: select_answer is part of the MultipleChoiceSolver base class and uses rerank internally
a = solver.select_answer("what is the speed of light", [
    "very fast", "10m/s", "the speed of light is C"
])
print(a)  # the speed of light is C
```

#### FlashRankEvidenceSolverPlugin

FlashRankEvidenceSolverPlugin is designed to extract the most relevant sentence from a text passage that answers a given
question. This plugin uses the FlashRank algorithm to evaluate and rank sentences based on their relevance to the query.

In text extraction and machine comprehension tasks, FlashRankEvidenceSolverPlugin enables the identification of specific
sentences within a larger body of text that directly address a user's query.

For example, in a scenario where a user queries about the number of rovers exploring Mars, FlashRankEvidenceSolverPlugin
scans the provided text passage, ranks sentences based on their relevance, and extracts the most informative sentence.

```python
from ovos_flashrank_solver import FlashRankEvidenceSolverPlugin

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
# 2024-07-22 15:05:14.209 - OVOS - __main__:load_corpus:61 - DEBUG - indexed 5 documents
# 2024-07-22 15:05:14.209 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 1 (score: 1.39238703250885): NASA currently has two rovers (Curiosity and Perseverance), one lander (InSight), and one helicopter (Ingenuity) exploring the surface of Mars.
# 2024-07-22 15:05:14.210 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 2 (score: 0.38667747378349304): Mars is one of the most explored bodies in our solar system, and it's the only planet where we've sent rovers to roam the alien landscape.
# 2024-07-22 15:05:14.210 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 3 (score: 0.15732118487358093): Mars is the fourth planet from the Sun.
# 2024-07-22 15:05:14.210 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 4 (score: 0.10177625715732574): Mars is also a dynamic planet with seasons, polar ice caps, canyons, extinct volcanoes, and evidence that it was even more active in the past.
# 2024-07-22 15:05:14.210 - OVOS - __main__:retrieve_from_corpus:70 - DEBUG - Rank 5 (score: 0.0): It is a dusty, cold, desert world with a very thin atmosphere.
# Query: how many rovers are currently exploring Mars
# Answer: NASA currently has two rovers (Curiosity and Perseverance), one lander (InSight), and one helicopter (Ingenuity) exploring the surface of Mars.

```

In this example, `FlashRankEvidenceSolverPlugin` effectively identifies and retrieves the most relevant sentence from
the provided text that answers the query about the number of rovers exploring Mars.
This capability is essential for applications requiring information extraction from extensive textual content, such as
automated research assistants or content summarizers.
