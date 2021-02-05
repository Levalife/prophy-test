def parse_text(text):
    if text:
        return dict(id=text[0], content=text[1])


def parse_keyphrase(keyphrase):
    if keyphrase:
        return dict(id=keyphrase[0], text_id=keyphrase[1], keyphrase=keyphrase[2], wiki_url=keyphrase[3],
                    is_exists=keyphrase[4], is_disambiguation=keyphrase[5])


def parse_keyphrase_ranked(keyphrase):
    if keyphrase:
        return dict(keyphrase=keyphrase[0], rank=keyphrase[1])

