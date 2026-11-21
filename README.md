# Understanding Users' Perceptions of Client-Side Modifications and Anti-Cheat Engines in Social XR

Code and supporting files for our paper "Understanding Users' Perceptions of Client-Side Modifications and Anti-Cheat Engines in Social XR", accepted to ACM SIGSAC Conference on Computer and Communications Security (CCS) 2026.

View the [Artifact Appendix](./Artifact-Appendix.pdf) for more details.

We do not release the Reddit data or the trained relevance classifier built on it due to Reddit's content policy.

Please cite our work as follows for any purpose of usage.

```bibtex
@inproceedings{mohammadi2026understanding,
  title={Understanding Users' Perceptions of Client-Side Modifications and Anti-Cheat Engines in Social {XR}},
  author={Mohammadi, Iman and Ali, Mutahar and Farrukh, Habiba},
  booktitle={Proceedings of the 2026 ACM SIGSAC Conference on Computer and Communications Security},
  pages={2030--2044},
  year={2026},
  doi={10.1145/3830454.3846683}
}
```

## Contents

| File | Description |
| --- | --- |
| `codebook.csv` | Codebook labels and their definitions. |
| `keywords.csv` | Keywords used to build the annotation sample. |
| `labeling_guide.md` | Guide followed by annotators. |
| `labeling_prompts.py` | Prompts for the multi-label classifier. |
| `events.csv` | List of events used in the regression analysis. |
| `requirements.txt` | Python package requirements. |
| `relevance_classifier.py` | Script for splitting the annotated posts and training and evaluating the relevance classifier. |
| `evaluate_relevance_classifier.py` | Script for evaluating an existing relevance classifier checkpoint on the test split. |
| `apply_relevance_classifier.py` | Script for running the trained classifier over the full corpus. |
| `multilabel_classifier.py` | LLM-based multi-label classifier. |
| `evaluate_labels.py` | Script for evaluating the LLM-based multi-label classifier. |
| `prevalence_analysis.py` | Script for computing how often each codebook label appears. |
| `regression_analysis.py` | Script for interrupted time-series regression analysis. |
| `plot_figure2.py` | Script for regenerating Figure 2 from the computed prevalences. |
| `plot_figure3.py` | Script for regenerating Figure 3 from the retained associations. |
| `results/` | Results for comparison between different models for classification and different window sizes for the regression analysis. |


## Requirements

Python 3.10 or newer.

```
pip install -r requirements.txt
```

Training the relevance classifier needs a GPU. Everything else runs on CPU.

The scripts read and write the private component in `data/`. Copy its files into a `data/`
directory alongside the scripts before running anything. Re-running an optional step overwrites
the provided file it produces, so keep a copy of the archive if you want the originals back.

`multilabel_classifier.py` reads the API key from the environment:

```
export GEMINI_API_KEY=your_key
```

## Running the pipeline

**1. Train and evaluate the relevance classifier.** Fine-tune DeBERTa-v3-base on the 1,250 manually annotated posts. The data is split 80/20 into train and test; the split is unstratified with a fixed seed, so it is identical on every machine, and both halves are written to `data/relevance_train_1000.csv` and `data/relevance_test_250.csv`.

```
python relevance_classifier.py
```

To evaluate a checkpoint without (re-)training, run:

```
python evaluate_relevance_classifier.py
```

It recomputes the same split and scores the same test posts, so the numbers match step 1.

**2. Apply it to the full corpus.** Classify every post using the relevance classifier to identify client-security-related posts.

```
python apply_relevance_classifier.py
```

**3. LLM-based Multi-Label Classifier.** Run the multi-label classifier to assign codes from the codebook to all client-security related posts.

```
python multilabel_classifier.py
```

Uses a separate API call and prompt (with few-shot examples) for each label. Progress is cached, so an interrupted run picks up where it stopped.

**4. Evaluate the Multi-Label Classifier.** Evaluate the multi-label classifier on 250 manually annotated posts.

```
python evaluate_labels.py
```

Outputs per-label and weighted average results.

**5. Compute theme prevalence.** How often each codebook label appears across the labeled posts.

```
python prevalence_analysis.py
```

Percentages are over posts carrying at least one label, so they sum to more than 100%.

To regenerate Figure 2 from those percentages, run:

```
python plot_figure2.py
```

**6. Run the interrupted time-series regression analysis.** Fit a segmented OLS around each event.

```
python regression_analysis.py --window 14
```

Results for window sizes of +/- 7, 14, and 30 days are included in `results/`.

To regenerate Figure 3, run:

```
python plot_figure3.py --window 14
```

`results/regression_analysis/retained_associations_w14.csv` lists the associations retained after the manual review described in the paper, with the fold change, pre- and post-event means, and the regression coefficient, p-value and corrected q-value for each. `regression_analysis.py` writes the complete set of tests, so the excluded pairs can be derived by comparison.

## License

- Code: [MIT License](LICENSE)
- Text, figures, and non-code artifacts: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
