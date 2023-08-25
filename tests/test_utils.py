import pytest
from typo_corrector.utils import create_hotkey_str, pipeline


@pytest.mark.parametrize(
    "use_ctrl, use_alt, use_shift, use_super, char, expected",
    [
        (True, False, False, False, 'a', '<ctrl>+a'),
        (False, True, False, False, 'b', '<alt>+b'),
        (True, True, False, False, 'c', '<ctrl>+<alt>+c'),
        (False, False, True, False, 'd', '<shift>+d'),
        (True, False, True, False, 'e', '<ctrl>+<shift>+e'),
        (False, True, True, False, 'f', '<alt>+<shift>+f'),
        (True, True, True, False, 'g', '<ctrl>+<alt>+<shift>+g'),
        (False, False, False, True, 'h', '<cmd>+h'),
        (True, False, False, True, 'i', '<cmd>+<ctrl>+i'),
        (False, True, False, True, 'j', '<cmd>+<alt>+j'),
        (True, True, False, True, 'k', '<cmd>+<ctrl>+<alt>+k'),
        (False, False, True, True, 'l', '<cmd>+<shift>+l'),
        (True, False, True, True, 'm', '<cmd>+<ctrl>+<shift>+m'),
        (False, True, True, True, 'n', '<cmd>+<alt>+<shift>+n'),
        (True, True, True, True, 'o', '<cmd>+<ctrl>+<alt>+<shift>+o'),
    ],
)
def test_create_hotkey_str(use_ctrl, use_alt, use_shift, use_super, char, expected):  # noqa
    # preparation
    sep = expected[-2]
    # execute
    result = create_hotkey_str(use_ctrl, use_alt, use_shift, use_super, char)
    # assert
    # NOTE: the order of the keys is irrelevant
    assert set(result.split(sep)) == set(expected.split(sep))
    # NOTE: the last key must be a letter
    assert result[-2] == expected[-2]
    assert result[-1] == expected[-1]


def assert_actual_eq_expected(
    actual,
    expected,
    return_value: bool = False,
    comparison_with_is: bool = False,
):
    if comparison_with_is:
        assert actual is expected
    else:
        assert actual == expected
    if return_value:
        return actual


@pytest.mark.parametrize(
    'input_args,input_kwargs,funcs,expected_results_for_funcs,expected',
    [
        (
            [],
            {},
            [],
            [],
            None,
        ),
        (
            [1],
            {},
            [lambda *args, **kwargs: args[0] + 1],
            [2],
            2,
        ),
        (
            [100],
            {},
            [
                lambda *args, **kwargs: args[0] + 1,
                lambda *args, **kwargs: args[0] + 10,
            ],
            [101, 111],
            111,
        ),
        (
            [1000, 2, 3],
            {"hoge": "fuga"},
            [
                lambda *inpt, **kwargs: 2 * inpt[0],
                lambda result, *inpt, **kwargs: result + 2*inpt[0],
                lambda result, *inpt, **kwargs: result + 3*inpt[0],
            ],
            [2000, 4000, 7000],
            7000,
        ),
        (
            [1000, 2, 3],
            {"hoge": "fuga"},
            [
                lambda *inpt, **kwargs: 2 * inpt[0],
                lambda result, *inpt, **kwargs: result + 2*inpt[0],
                lambda result, *inpt, **kwargs: None,
                lambda result, *inpt, **kwargs: result + 3*inpt[0],
            ],
            [2000, 4000, None, 7000],
            7000,
        ),
    ],
)
def test_pipeline(
    input_args,
    input_kwargs,
    funcs,
    expected_results_for_funcs,
    expected,
):
    # validation
    assert len(funcs) == len(expected_results_for_funcs)
    if not expected_results_for_funcs:
        assert expected is None

    # preparation
    def wrap_f_with_assertion(f, e):
        def _wrapped(*args, **kwargs):
            return assert_actual_eq_expected(
                f(*args, **kwargs),
                e,
                return_value=True,
                comparison_with_is=e is None,
            )
        return _wrapped

    funcs = [
        wrap_f_with_assertion(f, e)
        for f, e in zip(funcs, expected_results_for_funcs)
    ]
    p = pipeline(*funcs)
    # execute
    result = p(*input_args, **input_kwargs)
    # assert
    if expected is not None:
        result == expected
    else:
        assert result is None
