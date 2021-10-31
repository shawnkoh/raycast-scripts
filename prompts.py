import ankify
import md_parser

SOURCE_ATTRIBUTE = 'data-source'

class BasicPrompt:
    def __init__(self, question_md: str, answer_md: str or None, source_attribute=SOURCE_ATTRIBUTE):
        self.question_md = question_md.strip()
        if answer_md:
            self.answer_md = answer_md.strip()
        else:
            self.answer_md = None

        self.source_attribute = source_attribute

    @classmethod
    def from_anki_note(cls, note, source_attribute=SOURCE_ATTRIBUTE):
        question_field = note.fields[0]
        if not question_field:
            return None

        question_md = md_parser.extract_data(question_field, source_attribute)
        if not question_md:
            question_md = md_parser.html_to_markdown(question_field)
        if not question_md:
            return None

        answer_md = None
        if answer_field := note.fields[1]:
            answer_md = md_parser.extract_data(answer_field, source_attribute)
            if not answer_md:
                answer_md = md_parser.html_to_markdown(answer_field)
        
        return cls(question_md, answer_md, source_attribute)

    def question_field(self):
        html = md_parser.markdown_to_html(self.question_md)
        field = md_parser.insert_data(html, self.source_attribute, self.question_md)
        return field

    def answer_field(self):
        if not self.answer_md:
            return ""
        html = md_parser.markdown_to_html(self.answer_md)
        field = md_parser.insert_data(html, self.source_attribute, self.answer_md)
        return field

    def to_anki_note(self):
        note = ankify.collection.new_note(ankify.basic_notetype)
        note.fields[0] = self.question_field()
        note.fields[1] = self.answer_field()
        return note

class ClozePrompt:
    def __init__(self, stripped_md: str, clozed_md: str, source_attribute=SOURCE_ATTRIBUTE):
        self.stripped_md = stripped_md.strip()
        self.clozed_md = clozed_md.strip()
        self.source_attribute = source_attribute

    @classmethod
    def from_anki_note(cls, note, source_attribute=SOURCE_ATTRIBUTE):
        field = note.fields[0]
        if not field:
            return None

        md = md_parser.html_to_markdown(field)

        stripped_md = None
        clozed_md = md_parser.replace_anki_cloze_with_smart_cloze(md)

        stripped_md = md_parser.extract_data(field, source_attribute)
        if not stripped_md:
            stripped_md = md_parser.strip_anki_cloze(md)

        return cls(stripped_md, clozed_md, source_attribute)

    def field(self):
        html = md_parser.markdown_to_html(self.clozed_md)
        field = md_parser.insert_data(html, self.source_attribute, self.stripped_md)
        return field

    def to_anki_note(self):
        note = ankify.collection.new_note(ankify.basic_notetype)
        note.fields[0] = self.field()
        return note
