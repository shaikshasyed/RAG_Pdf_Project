import re


def sentence_chunk(text):
    """
    Split text into sentences.
    """

    sentences = re.split(r'(?<=[.!?])\s+', text)

    return sentences