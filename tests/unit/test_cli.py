from unittest.mock import patch

from mcpygen.cli import main


class TestApigenAsyncFlag:
    def test_async_flag_passed_to_generate(self):
        """The --async flag should be forwarded to generate_mcp_sources."""
        with (
            patch("mcpygen.cli.generate_mcp_sources", return_value=[]) as mock_generate,
            patch(
                "sys.argv",
                ["mcpygen", "apigen", "--server-name", "x", "--server-params", "{}", "--root-dir", "/tmp", "--async"],
            ),
        ):
            main()

        mock_generate.assert_called_once()
        assert mock_generate.call_args.kwargs["async_api"] is True

    def test_async_flag_defaults_to_false(self):
        """Without --async, async_api=False should be forwarded."""
        with (
            patch("mcpygen.cli.generate_mcp_sources", return_value=[]) as mock_generate,
            patch(
                "sys.argv", ["mcpygen", "apigen", "--server-name", "x", "--server-params", "{}", "--root-dir", "/tmp"]
            ),
        ):
            main()

        mock_generate.assert_called_once()
        assert mock_generate.call_args.kwargs["async_api"] is False
