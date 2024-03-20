import numpy as np
import sklearn.metrics
import datasets
import ast
import re

from Levenshtein import distance

COLUMNS_TO_REMOVE=["question_id", "passage_title", "passage_wiki", "passage_id", "duplicate", "annotated_by", "question_formulation", "question_type", "entity_type", "entity_subtype", "split", "passage_source"]


def process_docs(dataset: datasets.Dataset):
    def _helper(doc):
      doc["answers"] = ast.literal_eval(doc['answers'])
      return doc

    used = set()

    return dataset.remove_columns(COLUMNS_TO_REMOVE).filter(lambda example: example["relevant"] and (example['passage_text'],example['question']) not in used and (used.add((example['passage_text'],example['question'])) or True)).map(_helper)


def process_docs_closed(dataset: datasets.Dataset):
    def _helper(doc):
      doc["answers"] = ast.literal_eval(doc['answers'])
      return doc

    used = set()

    return dataset.remove_columns(COLUMNS_TO_REMOVE).filter(lambda example: example["relevant"] and example['question'] not in used and (used.add(example['question']) or True)).map(_helper)

def target(example):
    return example['answers']


# For non-numerical questions, we will assess textual similarity. To that end, a Levenshtein distance will be computed between the two (lowercased) strings and if it is less than ½ of the length of the gold standard answer, we accept the candidate answer.

# For numerical questions (e.g. In which year…), we will assess numerical similarity. Specifically, we will use a regular expression to extract a sequence of characters that could be interpreted as a number. If such sequences can be found in both answers and represent the same number, we accept the prediction.


NUMBER = re.compile(r'[-]?\d[\d,]*[\.\,]?[\d{2}]*')

def get_number(s):
    m=NUMBER.search(s)
    if m:
        return m.group(0).replace(",", ".")
    else:
        return None

def levenshtein(predictions, references):
    _prediction = predictions[0][0].lower()
    prediction_number = get_number(_prediction)

    _prediction = re.sub('\. ?(</s>) ?$','',_prediction)

    for reference in references:
        reference_number = get_number(reference)

        if reference_number is not None:
            if reference_number == prediction_number:
                return 1
        else:
            ld = distance(_prediction, reference.lower())
            if ld<len(reference)/2:
                return 1
    return 0


def agg_levenshtein(items):
    return sum(items)/len(items)
