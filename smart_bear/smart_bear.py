from smart_bear.anki.prompts import BasicPrompt, ClozePrompt
from smart_bear.markdown import md_parser


def extract_basic_prompts(md) -> dict[str, BasicPrompt]:
    basic_prompts = dict()
    for question_md, answer_md in md_parser.extract_basic_prompts(md).items():
        basic_prompts[question_md] = BasicPrompt(question_md, answer_md)
    return basic_prompts

def extract_cloze_prompts(md) -> dict[str, ClozePrompt]:
    cloze_prompts = dict()   
    for stripped_md, clozed_md in md_parser.extract_cloze_prompts(md).items():
        cloze_prompts[stripped_md] = ClozePrompt(stripped_md, clozed_md)
    return cloze_prompts

def import_markdowns(urls):
    import_basic_prompts = dict()
    import_cloze_prompts = dict()
    for url in urls:
        with open(url, "r") as file:
            md_text = file.read()
            md_text = md_parser.strip_title(md_text)
            md_text = md_parser.strip_backlink_blocks(md_text)

            basic_prompts = extract_basic_prompts(md_text)
            import_basic_prompts = import_basic_prompts | basic_prompts

            cloze_prompts = extract_cloze_prompts(md_text)
            import_cloze_prompts = import_cloze_prompts | cloze_prompts
    return import_basic_prompts, import_cloze_prompts
