# FlashRankMultipleChoiceSolver for OVOS

The `FlashRankMultipleChoiceSolver` plugin is designed for the Open Voice OS (OVOS) platform to help select the best answer to a question from a list of options. This plugin utilizes the FlashRank library to evaluate and rank multiple-choice answers based on their relevance to the given query.

## Features

- **Rerank Options**: Reranks a list of options based on their relevance to the query.
- **Customizable Model**: Allows the use of different ranking models.
- **Seamless Integration**: Designed to work with OVOS plugin manager.

### Important Note on FlashRank and Llama-CPP Compatibility

Installing FlashRank can lead to a downgrade of the `llama-cpp-python` version, which is critical for GPU support and performance, especially for large language models (LLMs). This issue is tracked in [FlashRank's GitHub repository](https://github.com/PrithivirajDamodaran/FlashRank/issues/29).

**Workaround for GPU Support with `llama-cpp-python`:**

If you need GPU support with `llama-cpp-python`, you might need to reinstall it after installing flashrank with specific CMake arguments:
```bash
CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip install llama-cpp-python --force-reinstall --no-cache-dir
```

Be aware that installing FlashRank may undo these custom installations

## Usage

### Example Usage

```python
if __name__ == "__main__":
    from flashrank_multiple_choice_solver import FlashRankMultipleChoiceSolver

    p = FlashRankMultipleChoiceSolver()
    a = p.rerank("what is the speed of light", [
        "very fast", "10m/s", "the speed of light is C"
    ])
    print(a)
    # Expected output:
    # [(0.999819, 'the speed of light is C'),
    #  (2.7686672e-05, 'very fast'),
    #  (1.2555749e-05, '10m/s')]

    a = p.select_answer("what is the speed of light", [
        "very fast", "10m/s", "the speed of light is C"
    ])
    print(a) # Expected output: the speed of light is C
```

## Configuration

The `FlashRankMultipleChoiceSolver` can be configured to use different ranking models. By default, it uses the `ms-marco-TinyBERT-L-2-v2` model. You can specify a different model in the configuration if needed.

Example configuration:
```json
{
    "model": "desired-model-name"
}
```

## Available Models

The following models are available for use with the `FlashRankMultipleChoiceSolver`:

| Model Name                   | Description                                                                                                   |
|------------------------------|---------------------------------------------------------------------------------------------------------------|
| ms-marco-TinyBERT-L-2-v2     | (default) [Model card](https://www.modelcards.com/ms-marco-TinyBERT-L-2-v2)                                     |
| ms-marco-MiniLM-L-12-v2      | [Model card](https://www.modelcards.com/ms-marco-MiniLM-L-12-v2)                                               |
| rank-T5-flan                 | Best non cross-encoder reranker [Model card](https://www.modelcards.com/rank-T5-flan)                          |
| ms-marco-MultiBERT-L-12      | Multi-lingual, supports 100+ languages                                                                         |
| ce-esci-MiniLM-L12-v2        | FT on Amazon ESCI dataset (This is interesting because most models are FT on MSFT MARCO Bing queries) [Model card](https://www.modelcards.com/ce-esci-MiniLM-L12-v2) |
| rank_zephyr_7b_v1_full       | 4-bit-quantised GGUF [Model card](https://www.modelcards.com/rank_zephyr_7b_v1_full) (Offers very competitive performance, with large context window and relatively faster for a 4GB model) |
