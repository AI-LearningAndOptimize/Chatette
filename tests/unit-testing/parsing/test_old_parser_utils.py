"""
Test module.
Test functionalities present in module `chatette.parsing.old_parser_utils`.
"""

import pytest

from chatette.parsing.old_parser_utils import *
from chatette.parsing.parser_utils import SubRuleType

class TestGetTopLevelLineType(object):
    def test_incorrect_lines(self):
        lines = ["something", "nothing", "\tsomething incorrect", "a\t"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) is None

    def test_empty_lines(self):
        lines = ["", "  ", "\t", "\t\t  \t"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) == LineType.empty

    def test_old_comment_lines(self):
        lines = ["\t;comment", ";comment"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) == LineType.comment

    def test_new_comment_lines(self):
        lines = ["\t//comment", "//comment\t"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) == LineType.comment
    
    def test_alias_lines(self):
        lines = ["~[alias]", "~[];comment", "~[alias] // comment\t"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) == LineType.alias_declaration

    def test_slot_lines(self):
        lines = ["@[slot]", "@[];comment", "@[slot] // comment\t"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) == LineType.slot_declaration

    def test_intent_lines(self):
        lines = ["%[intent]", "%[];comment", "%[intent] // comment\t"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) == LineType.intent_declaration

    def test_include_lines(self):
        lines = ["|include", "|file//comment", "|filename ; comment"]
        for l in lines:
            assert get_top_level_line_type(l, l.lstrip()) == LineType.include_file


class TestIsUnitStart(object):
    def test_empty(self):
        assert not is_unit_start("")

    def test_not_unit_start_word(self):
        words = ["word", "\tother", "|includedfile"]
        for w in words:
            assert not is_unit_start(w)

    def test_unit_start_word(self):
        words = ["[unit]", "~[alias]", "@[slot]", "%[intent]"]
        for w in words:
            assert is_unit_start(w)


class TestIsChoice(object):
    def test_empty(self):
        assert not is_choice("")
    
    def test_not_choice_word(self):
        words = ["word", "[unit]", "~[alias]", "False", "\tword"]
        for w in words:
            assert not is_choice(w)

    def test_choice_words(self):
        words = ["{choice}", "{a/b}", "{"]
        # The last one might be considered not a valid choice
        # (not what is currently done in `is_choice`)
        for w in words:
            assert is_choice(w)


class TestIsWord(object):
    def test_empty(self):
        assert not is_word("")
    
    def test_not_word(self):
        strings = ["[unit]", "~[alias]", "@[slot]", "%[intent]", "{choice/a}",
                   " ", "\t\t"]
        for s in strings:
            assert not is_word(s)
    
    def test_word(self):
        words = ["word", "a", "other things", "test.", "?", "!"]
        for w in words:
            assert is_word(w)


class TestGetUnitType(object):
    def test_empty(self):
        with pytest.raises(RuntimeError,
                           message="Empty string does not raise an exception "+
                                   "when trying to get its unit type."):
            get_unit_type("")
    
    def test_not_units(self):
        strings = ["word", "?", "several words"]
        for s in strings:
            with pytest.raises(RuntimeError, 
                               message="Strings that are not units do not "+
                                       "raise an exception when trying to get "+
                                       "its unit type."):
                get_unit_type(s)
    
    def test_units(self):
        unit = "[unit]"
        assert get_unit_type(unit) == SubRuleType.word_group
        unit = "[word group]"
        assert get_unit_type(unit) == SubRuleType.word_group
        unit = "~[alias] //comment"
        assert get_unit_type(unit) == SubRuleType.alias
        unit = "@[slot]"
        assert get_unit_type(unit) == SubRuleType.slot
        unit = "%[intent]"
        assert get_unit_type(unit) == SubRuleType.intent
        unit = "{choice/choice 2?}"
        assert get_unit_type(unit) == SubRuleType.choice
        


class TestFindNbTrainingExamplesAsked(object):
    def test_empty(self):
        assert find_nb_training_examples_asked("") is None

    def test_no_intent(self):
        strings = ["// comment", "word", "\tseveral words", "[word group]",
                   "|includedfile", "sentence with nb in parentheses (12)"]
        for s in strings:
            assert find_nb_training_examples_asked(s) is None
    
    def test_no_nb_asked(self):
        intents = ["%[intent]", "%[intent in several words]", "%[test]()",
                   "%[intent] // comment"]
        for i in intents:
            assert find_nb_training_examples_asked(i) is None
    
    def test_several_nb(self):
        # NOTE: The strings are very specific to the pattern being matched
        strings = ["%[intent](1)('training':'5')", "](1)](2)",
                   "'training':5,train: 8", "train:120 ('training: 3')"]
        for s in strings:
            with pytest.raises(SyntaxError,
                               message="An intent with several numbers of "+
                                       "examples to generate should raise "+
                                       "a `SyntaxError`."):
                print(find_nb_training_examples_asked(s))

    def test_intents(self):
        # NOTE: The strings are very specific to the pattern being matched
        intents = ["%[intent](42)", "](42)", "'training':42", "train : '42'",
                   "'train: 42'", "training :42, test: 58", "train:42,'test':38"]
        for i in intents:
            assert find_nb_training_examples_asked(i) == 42


class TestFindNbTestingExamplesAsked(object):
    def test_empty(self):
        assert find_nb_testing_examples_asked("") is None

    def test_no_intent(self):
        strings = ["// comment", "word", "\tseveral words", "[word group]",
                   "|includedfile", "sentence with nb in parentheses (12)"]
        for s in strings:
            assert find_nb_testing_examples_asked(s) is None
    
    def test_no_nb_asked(self):
        intents = ["%[intent]", "%[intent in several words]", "%[test]()",
                   "%[intent] // comment"]
        for i in intents:
            assert find_nb_testing_examples_asked(i) is None
    
    def test_several_nb(self):
        # NOTE: The strings are very specific to the pattern being matched
        strings = ["%[intent](test: 1)('testing':'5')", "test:1 'testing : 2'",
                   "'testing':5,test: 8", "test:120 ('testing: 3')"]
        for s in strings:
            with pytest.raises(SyntaxError,
                               message="An intent with several numbers of "+
                                       "examples to generate should raise "+
                                       "a `SyntaxError`."):
                print(find_nb_testing_examples_asked(s))

    def test_intents(self):
        # NOTE: The strings are very specific to the pattern being matched
        intents = ["%[intent](test:42)", "'testing':42", "test : '42'",
                   "'test: 42'", "training :58, test: 42", "test:42,'train':38"]
        for i in intents:
            assert find_nb_testing_examples_asked(i) == 42