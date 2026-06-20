---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:30
- loss:MultipleNegativesRankingLoss
base_model: BAAI/bge-m3
widget:
- source_sentence: 거래량 데이터 조회
  sentences:
  - '2024년 01월 03일 하이트진로(000080, KOSPI) 주가: 종가 22,500원 (전일대비 +200원, +0.90%), 시가 22,300원,
    고가 22,550원, 저가 22,150원, 거래량 181,964주, 시가총액 15,780억원'
  - '2024년 01월 02일 삼성전자(005930, KOSPI) 주가: 종가 74,300원 (전일대비 +500원, +0.68%), 시가 74,000원,
    고가 75,000원, 저가 73,800원, 거래량 10,234,567주, 시가총액 4,432,690억원'
  - '2024년 12월 31일 카카오뱅크(323410, KOSPI) 주가: 종가 22,300원 (전일대비 -100원, -0.45%), 시가 22,400원,
    고가 22,700원, 저가 22,200원, 거래량 1,567,890주, 시가총액 105,821억원'
- source_sentence: SK하이닉스 최근 종가
  sentences:
  - '2024년 01월 02일 하이트진로(000080, KOSPI) 주가: 종가 22,300원 (전일대비 -200원, -0.89%), 시가 22,500원,
    고가 22,550원, 저가 22,300원, 거래량 203,536주, 시가총액 15,639억원'
  - '2024년 12월 31일 삼성전자(005930, KOSPI) 주가: 종가 53,400원 (전일대비 -200원, -0.37%), 시가 53,600원,
    고가 54,000원, 저가 53,200원, 거래량 12,345,678주, 시가총액 3,187,440억원'
  - '2024년 12월 31일 SK하이닉스(000660, KOSPI) 주가: 종가 171,000원 (전일대비 +1,500원, +0.88%), 시가
    169,500원, 고가 172,000원, 저가 169,000원, 거래량 3,210,456주, 시가총액 1,244,880억원'
- source_sentence: 코스닥 성장주 에코프로 주가
  sentences:
  - '2024년 01월 15일 하이트진로(000080, KOSPI) 주가: 종가 22,100원 (전일대비 +300원, +1.38%), 시가 21,900원,
    고가 22,250원, 저가 21,750원, 거래량 143,762주, 시가총액 15,499억원'
  - '2024년 01월 08일 하이트진로(000080, KOSPI) 주가: 종가 22,150원 (전일대비 -50원, -0.23%), 시가 22,100원,
    고가 22,400원, 저가 22,100원, 거래량 84,822주, 시가총액 15,534억원'
  - '2024년 12월 31일 에코프로(086520, KOSDAQ) 주가: 종가 89,200원 (전일대비 +1,200원, +1.36%), 시가
    88,000원, 고가 90,500원, 저가 87,500원, 거래량 3,456,789주, 시가총액 65,820억원'
- source_sentence: 삼성전자 12월 주가는?
  sentences:
  - '2024년 01월 05일 하이트진로(000080, KOSPI) 주가: 종가 22,200원 (전일대비 +0원, +0.00%), 시가 22,200원,
    고가 22,550원, 저가 22,100원, 거래량 125,140주, 시가총액 15,569억원'
  - '2024년 12월 31일 삼성전자(005930, KOSPI) 주가: 종가 53,400원 (전일대비 -200원, -0.37%), 시가 53,600원,
    고가 54,000원, 저가 53,200원, 거래량 12,345,678주, 시가총액 3,187,440억원'
  - '2024년 01월 04일 하이트진로(000080, KOSPI) 주가: 종가 22,200원 (전일대비 -300원, -1.33%), 시가 22,500원,
    고가 22,600원, 저가 22,050원, 거래량 155,275주, 시가총액 15,569억원'
- source_sentence: 셀트리온 바이오주 주가
  sentences:
  - '2024년 06월 10일 현대차(005380, KOSPI) 주가: 종가 248,000원 (전일대비 +8,000원, +3.33%), 시가 240,000원,
    고가 252,500원, 저가 239,500원, 거래량 1,234,567주, 시가총액 529,336억원'
  - '2024년 01월 10일 하이트진로(000080, KOSPI) 주가: 종가 22,050원 (전일대비 -100원, -0.45%), 시가 22,150원,
    고가 22,200원, 저가 21,850원, 거래량 129,971주, 시가총액 15,464억원'
  - '2024년 12월 31일 셀트리온(068270, KOSPI) 주가: 종가 155,700원 (전일대비 +700원, +0.45%), 시가 155,000원,
    고가 156,500원, 저가 154,500원, 거래량 456,789주, 시가총액 220,016억원'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer based on BAAI/bge-m3

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3). It maps sentences & paragraphs to a 1024-dimensional dense vector space and can be used for retrieval.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) <!-- at revision 5617a9f61b028005a4858fdac845db406aefb181 -->
- **Maximum Sequence Length:** 8192 tokens
- **Output Dimensionality:** 1024 dimensions
- **Similarity Function:** Cosine Similarity
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'XLMRobertaModel'})
  (1): Pooling({'embedding_dimension': 1024, 'pooling_mode': 'cls', 'include_prompt': True})
  (2): Normalize({})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```
Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    '셀트리온 바이오주 주가',
    '2024년 12월 31일 셀트리온(068270, KOSPI) 주가: 종가 155,700원 (전일대비 +700원, +0.45%), 시가 155,000원, 고가 156,500원, 저가 154,500원, 거래량 456,789주, 시가총액 220,016억원',
    '2024년 01월 10일 하이트진로(000080, KOSPI) 주가: 종가 22,050원 (전일대비 -100원, -0.45%), 시가 22,150원, 고가 22,200원, 저가 21,850원, 거래량 129,971주, 시가총액 15,464억원',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 1024]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.7582, 0.1570],
#         [0.7582, 1.0000, 0.2225],
#         [0.1570, 0.2225, 1.0000]])
```
<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 30 training samples
* Columns: <code>anchor</code> and <code>positive</code>
* Approximate statistics based on the first 30 samples:
  |          | anchor                                                                           | positive                                                                           |
  |:---------|:---------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|
  | type     | string                                                                           | string                                                                             |
  | modality | text                                                                             | text                                                                               |
  | details  | <ul><li>min: 6 tokens</li><li>mean: 8.67 tokens</li><li>max: 13 tokens</li></ul> | <ul><li>min: 74 tokens</li><li>mean: 77.73 tokens</li><li>max: 83 tokens</li></ul> |
* Samples:
  | anchor                         | positive                                                                                                                                                         |
  |:-------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>삼성전자 12월 주가는?</code>     | <code>2024년 12월 31일 삼성전자(005930, KOSPI) 주가: 종가 53,400원 (전일대비 -200원, -0.37%), 시가 53,600원, 고가 54,000원, 저가 53,200원, 거래량 12,345,678주, 시가총액 3,187,440억원</code>        |
  | <code>SK하이닉스 최근 종가</code>      | <code>2024년 12월 31일 SK하이닉스(000660, KOSPI) 주가: 종가 171,000원 (전일대비 +1,500원, +0.88%), 시가 169,500원, 고가 172,000원, 저가 169,000원, 거래량 3,210,456주, 시가총액 1,244,880억원</code> |
  | <code>삼성전자 거래량 가장 많았던 날</code> | <code>2024년 11월 15일 삼성전자(005930, KOSPI) 주가: 종가 56,800원 (전일대비 -3,200원, -5.34%), 시가 60,000원, 고가 60,100원, 저가 56,500원, 거래량 58,932,100주, 시가총액 3,390,120억원</code>      |
* Loss: [<code>MultipleNegativesRankingLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#multiplenegativesrankingloss) with these parameters:
  ```json
  {
      "scale": 20.0,
      "similarity_fct": "cos_sim",
      "gather_across_devices": false,
      "directions": [
          "query_to_doc"
      ],
      "partition_mode": "joint",
      "hardness_mode": null,
      "hardness_strength": 0.0
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 4
- `warmup_steps`: 0.1
- `use_cpu`: True
- `dataloader_pin_memory`: False

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 4
- `num_train_epochs`: 3
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0.1
- `optim`: adamw_torch_fused
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1.0
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 8
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: True
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: False
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: None
- `fsdp_config`: None
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch | Step | Training Loss |
|:-----:|:----:|:-------------:|
| 0.25  | 2    | 0.5785        |
| 0.5   | 4    | 1.3000        |
| 0.75  | 6    | 0.1355        |
| 1.0   | 8    | 0.1436        |
| 1.25  | 10   | 0.2517        |
| 1.5   | 12   | 0.1585        |
| 1.75  | 14   | 0.1688        |
| 2.0   | 16   | 0.5806        |
| 2.25  | 18   | 0.0013        |
| 2.5   | 20   | 0.9319        |
| 2.75  | 22   | 0.0752        |
| 3.0   | 24   | 0.4793        |


### Training Time
- **Training**: 1.4 minutes

### Framework Versions
- Python: 3.14.4
- Sentence Transformers: 5.6.0
- Transformers: 5.12.1
- PyTorch: 2.12.1+cu130
- Accelerate: 1.14.0
- Datasets: 5.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

#### MultipleNegativesRankingLoss
```bibtex
@misc{oord2019representationlearningcontrastivepredictive,
      title={Representation Learning with Contrastive Predictive Coding},
      author={Aaron van den Oord and Yazhe Li and Oriol Vinyals},
      year={2019},
      eprint={1807.03748},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/1807.03748},
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->