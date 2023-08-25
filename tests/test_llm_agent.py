from langchain.llms import OpenAI
from typo_corrector.llm_agent import LLMAgent


def test_llm_agent(mocker):

    # preparation
    expected = 'corrected'
    llm = mocker.MagicMock(spec=OpenAI)
    llm.predict.return_value = f'(pre){expected}'
    memory = mocker.MagicMock()
    agent = LLMAgent(
        llm=llm,
        memory=memory,
    )

    # test
    callback = mocker.MagicMock()
    callback.return_value = expected
    actual = agent.interact(
        pairs_of_header_body=[
            ('header1', 'body1'),
            ('header2', 'body2'),
        ],
        callback=callback,
    )

    # check
    llm.predict.assert_called_once()
    callback.assert_called_once_with(llm.predict.return_value)
    assert actual == expected
