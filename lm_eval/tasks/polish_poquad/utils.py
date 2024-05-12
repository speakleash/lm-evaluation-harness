""" Utility functions for the poquad task """
import re
from Levenshtein import distance


def doc_to_target(doc):
    answer_list = doc["answers"]["text"]
    if len(answer_list) > 0:
        answer = answer_list[0]
    else:
        answer = "bez odpowiedzi"
    return " " + answer

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
    _prediction = predictions[0][0].lower()
    prediction_number = get_number(_prediction)

    _prediction = re.sub('.? ?(</s>)* ?$', '', _prediction)

    for reference in references:
        reference_number = get_number(reference)

        if reference_number is not None:
            if reference_number == prediction_number:
                return 1
        else:
            ld = distance(_prediction, reference.lower())
            if ld < len(reference)/2:
                return 1
    return 0


def agg_levenshtein(items):
    return sum(items)/len(items)
