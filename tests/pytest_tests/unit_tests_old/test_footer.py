"""
footer tests.
"""

import re

import pytest
import wandb


def strip_upgrade_messages(message_lines):
    upgrade_messages = re.compile(
        r"(wandb: ERROR wandb version .* has been retired!  Please upgrade\."
        r"|wandb: wandb version .* is available!  To upgrade, please run:"
        r"|wandb:  \$ pip install wandb --upgrade)"
    )
    return [line for line in message_lines if not upgrade_messages.match(line)]


@pytest.mark.parametrize("utfText", ["my first hint", ""])
@pytest.mark.parametrize("messageType", ["footer", ""])
@pytest.mark.parametrize("messageLevel", ["20", "", 20])
def test_footer_server_message(
    live_mock_server,
    test_settings,
    capsys,
    utfText,
    messageType,
    messageLevel,
):
    live_mock_server.set_ctx({"server_settings": True})
    server_messages = [
        {
            "utfText": utfText,
            "plainText": "my first hint",
            "htmlText": "",
            "messageType": messageType,
            "messageLevel": messageLevel,
        }
    ]
    live_mock_server.set_ctx({"server_messages": server_messages})

    test_settings.update({"disable_hints": False})
    with wandb.init(settings=test_settings) as run:
        run.log(dict(d=2))

    lines = capsys.readouterr().err.splitlines()
    lines = strip_upgrade_messages(lines)

    if messageType == "footer":
        assert (
            server_messages[0].get("utfText")
            or server_messages[0].get("plainText") in lines[-1]
        )
    else:
        assert "Find logs at:" in lines[-1]


@pytest.mark.parametrize(
    "server_messages",
    [
        [],
        None,
        [
            {
                "utfText": "utfText",
                "messageType": "footer",
            }
        ],
    ],
)
@pytest.mark.parametrize("server_settings", [False, None])
@pytest.mark.parametrize(
    "disable_hints",
    [
        True,
        False,
    ],
)
def test_footer_server_message_no_message(
    live_mock_server,
    test_settings,
    capsys,
    server_settings,
    server_messages,
    disable_hints,
):
    live_mock_server.set_ctx({"server_settings": server_settings})
    live_mock_server.set_ctx({"server_messages": server_messages})
    test_settings.update({"disable_hints": disable_hints})
    with wandb.init(settings=test_settings) as run:
        run.log(dict(d=2))

    lines = capsys.readouterr().err.splitlines()
    lines = strip_upgrade_messages(lines)
    assert "Find logs at:" in lines[-1]
