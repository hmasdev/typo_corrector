from typo_corrector.config import (
    Config,
    DEFAULT_CONFIG,
    Keybind,
    load_config,
    save_config,
)


def test_load_config(mocker):

    # pareparation
    mock_open = mocker.patch('builtins.open')
    mock_json_load = mocker.patch('json.load')

    path = 'path/to/config.json'
    expected = Config(
        activation_keybind=Keybind(use_ctrl=True, use_alt=True, use_shift=True, use_super=False, char='a'),  # noqa
        config_keybind=Keybind(use_ctrl=True, use_alt=True, use_shift=True, use_super=False, char='j'),  # noqa
        condition_str='condition',
        example_str='example',
    )

    mock_open.return_value.__enter__.return_value = 'file'
    mock_json_load.return_value = expected.model_dump()

    # validate
    assert expected != DEFAULT_CONFIG

    # execute
    actual = load_config(path)

    # assert
    assert actual == expected


def test_load_config_when_file_not_found(mocker):

    # prepare
    mock_save_config = mocker.patch('typo_corrector.config.save_config')  # noqa
    path = 'path/to/config.json'
    expected = DEFAULT_CONFIG

    # execute
    actual = load_config(path)

    # assert
    assert actual == expected
    mock_save_config.assert_called_once_with(expected, config_path=path)  # noqa


def test_save_config(mocker):

    # pareparation
    mock_open = mocker.patch('builtins.open')
    mock_json_dump = mocker.patch('json.dump')
    mock_open.return_value.__enter__.return_value = 'file'

    path = 'path/to/config.json'
    config = DEFAULT_CONFIG

    # execute
    save_config(config, config_path=path)

    # assert
    mock_open.assert_called_once_with(path, 'w', encoding='utf-8')
    mock_json_dump.assert_called_once_with(config.model_dump(), mock_open.return_value.__enter__.return_value, indent=4, ensure_ascii=False)  # noqa
