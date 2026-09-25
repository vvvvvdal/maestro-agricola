#!/usr/bin/env python3
import importlib.util
import json
import pathlib
import sys
import unittest

spec = importlib.util.spec_from_file_location("jev_local_proxy", pathlib.Path(__file__).with_name("jev_local_proxy.py"))
assert spec and spec.loader
proxy = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = proxy
spec.loader.exec_module(proxy)


class JevLocalProxyTest(unittest.TestCase):
    def test_accepts_only_the_transcript_field(self):
        self.assertEqual("volte", proxy.parse_client_request(b'{"transcript":"volte"}'))
        with self.assertRaises(proxy.ProxyError):
            proxy.parse_client_request(b'{"transcript":"volte","target":"plot-01"}')

    def test_payload_has_fixed_model_and_six_choices(self):
        payload = proxy.request_payload("cancele")
        self.assertEqual(proxy.MODEL, payload["model"])
        self.assertEqual(set(proxy.CRITERIA), set(payload["questions"][proxy.QUESTION_KEY]["criteria"]))

    def test_rejects_obvious_personal_data(self):
        for transcript in (
            "meu email e pessoa@exemplo.test",
            "ligue para 11987654321",
            "cpf 000.000.000-00",
            "cnpj 00.000.000/0000-00",
        ):
            with self.assertRaises(proxy.ProxyError) as raised:
                proxy.parse_client_request(json_payload(transcript))
            self.assertEqual("sensitive_transcript", raised.exception.code)

    def test_rejects_url_size_and_outside_remote_scope(self):
        cases = {
            "veja https://exemplo.test": "url_transcript",
            "x" * (proxy.MAX_TRANSCRIPT_CHARS + 1): "transcript_too_long",
            "qual a previsão do tempo amanhã": "outside_remote_scope",
        }
        for transcript, expected_code in cases.items():
            with self.assertRaises(proxy.ProxyError) as raised:
                proxy.parse_client_request(json_payload(transcript))
            self.assertEqual(expected_code, raised.exception.code)

    def test_accepts_short_operational_transcript(self):
        self.assertEqual("volte para a doca", proxy.parse_client_request(json_payload("volte para a doca")))

    def test_request_limit_counts_each_http_attempt(self):
        evaluator = proxy.JevProxy("test-key", max_requests=2)
        self.assertTrue(evaluator.reserve_http_attempt())
        self.assertTrue(evaluator.reserve_http_attempt())
        self.assertFalse(evaluator.reserve_http_attempt())


def json_payload(transcript: str) -> bytes:
    return json.dumps({"transcript": transcript}).encode()


if __name__ == "__main__":
    unittest.main()
