# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests some cases were completions need to be hidden."""

# Third party imports
from flaky import flaky
import pytest

from qtpy.QtCore import Qt


@pytest.mark.slow
@pytest.mark.first
@flaky(max_runs=5)
def test_automatic_completions_hide_complete(lsp_codeeditor, qtbot):
    """Test on-the-fly completion closing when already complete.

    Regression test for issue #11600 and pull requests #11824, #12140
    and #12710.
    """
    code_editor, _ = lsp_codeeditor
    completion = code_editor.completion_widget
    code_editor.toggle_code_snippets(False)

    code_editor.set_text('some = 0\nsomething = 1\n')
    cursor = code_editor.textCursor()
    code_editor.moveCursor(cursor.End)

    # Complete some -> [some, something]
    with qtbot.waitSignal(completion.sig_show_completions,
                          timeout=10000) as sig:
        qtbot.keyClicks(code_editor, 'some')
    assert "some" in [x['label'] for x in sig.args[0]]
    assert "something" in [x['label'] for x in sig.args[0]]

    # No completion for 'something' as already complete
    qtbot.keyClicks(code_editor, 'thing')
    qtbot.wait(500)
    assert completion.isHidden()
    qtbot.keyPress(code_editor, Qt.Key_Enter, delay=300)  # newline

    # Hide even within a function
    qtbot.keyClicks(code_editor, 'print(something')
    qtbot.wait(500)
    assert completion.isHidden()
    qtbot.keyClicks(code_editor, ')')
    qtbot.keyPress(code_editor, Qt.Key_Enter, delay=300)  # newline

    # Hide even inside comprehension
    qtbot.keyClicks(code_editor, 'a = {something')
    qtbot.wait(500)
    assert completion.isHidden()

    # Hide if removing spaces before a word
    code_editor.moveCursor(cursor.End)
    qtbot.keyPress(code_editor, Qt.Key_Enter)  # newline
    qtbot.keyClicks(code_editor, 'some')
    qtbot.keyPress(code_editor, Qt.Key_Enter)  # newline
    qtbot.keyClicks(code_editor, '  None')
    code_editor.moveCursor(cursor.End - 6)
    qtbot.keyPress(code_editor, Qt.Key_Backspace)
    qtbot.wait(2000)
    assert completion.isHidden()
    qtbot.keyPress(code_editor, Qt.Key_Backspace)
    qtbot.wait(2000)
    assert completion.isHidden()

    # Hide if removing spaces before a word even not at the start of line.
    code_editor.moveCursor(cursor.End)
    qtbot.keyPress(code_editor, Qt.Key_Enter)  # newline
    qtbot.keyClicks(code_editor, 'some +  some ')
    qtbot.keyPress(code_editor, Qt.Key_Left)
    qtbot.keyPress(code_editor, Qt.Key_Left)
    qtbot.keyPress(code_editor, Qt.Key_Left)
    qtbot.keyPress(code_editor, Qt.Key_Left)
    qtbot.keyPress(code_editor, Qt.Key_Left)
    qtbot.keyPress(code_editor, Qt.Key_Backspace)
    qtbot.wait(2000)
    assert completion.isHidden()

    code_editor.toggle_code_snippets(True)


@pytest.mark.slow
@pytest.mark.first
@flaky(max_runs=5)
def test_automatic_completions_widget_visible(lsp_codeeditor, qtbot):
    """
    Test on-the-fly completions when the widget is visible and the Backspace
    key is pressed.

    Regression test for PR #12710
    """
    code_editor, _ = lsp_codeeditor
    completion = code_editor.completion_widget
    code_editor.toggle_code_snippets(False)

    code_editor.set_text('import math')
    cursor = code_editor.textCursor()
    code_editor.moveCursor(cursor.End)
    qtbot.keyPress(code_editor, Qt.Key_Enter, delay=300)  # newline

    with qtbot.waitSignal(completion.sig_show_completions,
                          timeout=10000) as sig:
        qtbot.keyClicks(code_editor, 'math.aco')

    assert completion.isVisible()

    qtbot.keyPress(code_editor, Qt.Key_Backspace, delay=300)
    assert completion.isVisible()

    qtbot.keyPress(code_editor, Qt.Key_Backspace, delay=300)
    assert completion.isVisible()


if __name__ == '__main__':
    pytest.main(['test_completion.py', '--run-slow'])
