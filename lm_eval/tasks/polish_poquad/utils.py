""" Utility functions for the poquad task """
import re
from Levenshtein import distance
import datasets

COLUMNS_TO_REMOVE= []
BRAK_INFORMACJI =  "Brak informacji"
def process_docs_open(dataset: datasets.Dataset):
    def _helper(doc):
        if doc['is_impossible']:
            doc["answers"] = {'text': [BRAK_INFORMACJI], 'answer_start': [0], 'generative_answer': [BRAK_INFORMACJI]}
        return doc

    used = set()

    return dataset.remove_columns(COLUMNS_TO_REMOVE).filter(lambda example: (example['context'],example['question']) not in used and (used.add((example['context'],example['question'])) or True)).map(_helper)

def process_docs_open_positive(dataset: datasets.Dataset):
    def _helper(doc):
        if doc['is_impossible']:
            doc["answers"] = {'text': [BRAK_INFORMACJI], 'answer_start': [0], 'generative_answer': [BRAK_INFORMACJI]}
        return doc

    used = set()

    return dataset.remove_columns(COLUMNS_TO_REMOVE).filter(lambda example: (not example['is_impossible']) and (example['context'],example['question']) not in used and (used.add((example['context'],example['question'])) or True)).map(_helper)


def doc_to_target(doc):
    answer_list = doc["answers"]["text"]
    if len(answer_list) > 0:
        answer = answer_list[0]
    else:
        answer = "bez odpowiedzi"
    return " " + answer

def doc_to_target2(doc):
    # return doc['generative_answer']
    answer_list = doc["answers"]["generative_answer"]
    if len(answer_list) > 0:
        answer = answer_list[0]
    else:
        answer = BRAK_INFORMACJI
    return " " + answer


def doc_to_target_reranking(doc):
    return 0 if doc["is_impossible"] else 1


# For non-numerical questions, we will assess textual similarity.
# To that end, a Levenshtein distance will be computed between the two (lowercased) strings,
# and if it is less than ½ of the length of the gold standard answer, we accept the candidate answer.

# For numerical questions (e.g., In which year…), we will assess numerical similarity.
# Specifically, we will use a regular expression to extract a sequence of characters that could be interpreted as a number.
# If such sequences can be found in both answers and represent the same number, we accept the prediction.


NUMBER = re.compile(r'-?\d[\d,]*[.,]?[\d{2}]*')


def get_number(s):
    m = NUMBER.search(s)
    if m:
        return m.group().replace(",", ".")
    else:
        return None


def levenshtein(predictions, references):
    _prediction = predictions[0].lower().lstrip()
    prediction_number = get_number(_prediction)

    _prediction = re.sub('.? ?(</s>)* ?$', '', _prediction)

    for reference in references:
        reference_number = get_number(reference)

        if reference_number is not None:
            if reference_number == prediction_number:
                return 1
        else:
            ld = distance(_prediction, reference.lower().lstrip())
            if ld < len(reference)/2:
                return 1
    return 0


def agg_levenshtein(items):
    return sum(items)/len(items)
