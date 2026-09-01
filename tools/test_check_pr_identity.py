import unittest

import check_pr_identity as gate


def record(an=gate.CANONICAL[0], ae=gate.CANONICAL[1], cn=gate.CANONICAL[0], ce=gate.CANONICAL[1], message="Governed change"):
    return {"author_name": an, "author_email": ae, "committer_name": cn, "committer_email": ce, "message": message}


class PublicIdentityGateTests(unittest.TestCase):
    def test_canonical_commit_passes(self):
        self.assertEqual([], gate.inspect_commit(record()))

    def test_historical_bridge_identity_blocks_in_all_positions(self):
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(record(an="Bridge-Node-7", ae="bridge@" + "example.invalid")))
        self.assertIn("COMMITTER_NOT_AUTHORIZED", gate.inspect_commit(record(cn="Bridge Node 7", ce="bridge@" + "example.invalid")))
        for trailer in ("Co-authored-by", "Signed-off-by", "Reviewed-by", "Acked-by", "Tested-by", "Reported-by", "Helped-by", "Suggested-by"):
            with self.subTest(trailer=trailer):
                value = record(message=f"Change\n\n{trailer}: Bridge-Node-7 <bridge@{'example.invalid'}>")
                self.assertIn("IDENTITY_TRAILER_NOT_AUTHORIZED", gate.inspect_commit(value))

    def test_historical_numeric_id_blocks(self):
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(record(ae="291729790+Bridge-Node-7@" + "users.noreply.github.com")))

    def test_canonical_looking_wrong_numeric_id_blocks(self):
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(record(ae="291729790+GLOBAL-AI-GOVERNANCE@" + "users.noreply.github.com")))

    def test_foreign_numeric_noreply_blocks(self):
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(record(an="Other", ae="123+other@" + "users.noreply.github.com")))

    def test_arbitrary_noreply_is_not_trusted(self):
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(record(an="Other", ae="other@" + "noreply.example")))

    def test_prohibited_committer_blocks(self):
        self.assertIn("COMMITTER_NOT_AUTHORIZED", gate.inspect_commit(record(cn="Other", ce="other@" + "example.invalid")))

    def test_prohibited_identity_trailers_block(self):
        for trailer in ("Co-authored-by", "Signed-off-by", "Reviewed-by", "Acked-by", "Tested-by", "Reported-by", "Helped-by", "Suggested-by"):
            with self.subTest(trailer=trailer):
                value = record(message=f"Change\n\n{trailer}: Other <other@{'example.invalid'}>")
                self.assertIn("IDENTITY_TRAILER_NOT_AUTHORIZED", gate.inspect_commit(value))

    def test_approved_service_is_bounded(self):
        self.assertEqual([], gate.inspect_commit(record(cn="GitHub", ce="noreply@" + "github.com")))
        self.assertIn("COMMITTER_NOT_AUTHORIZED", gate.inspect_commit(record(cn="GitHub", ce="other@" + "noreply.github.com")))

    def test_authoritative_dependabot_fixture_passes(self):
        value = record(
            an=gate.DEPENDABOT[0],
            ae=gate.DEPENDABOT[1],
            cn="GitHub",
            ce="noreply@" + "github.com",
            message="Bump dependency\n\nSigned-off-by: dependabot[bot] <support@" + "github.com>",
        )
        self.assertEqual([], gate.inspect_commit(value))

    def test_dependabot_like_spoof_blocks(self):
        value = record(an="dependabot[bot]", ae="1+dependabot[bot]@" + "users.noreply.github.com")
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(value))

    def test_dependabot_support_address_is_trailer_specific(self):
        value = record(an="dependabot[bot]", ae="support@" + "github.com")
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(value))

    def test_unknown_service_and_malformed_trailer_block(self):
        self.assertIn("AUTHOR_NOT_AUTHORIZED", gate.inspect_commit(record(an="unknown[bot]", ae="2+unknown[bot]@" + "users.noreply.github.com")))
        self.assertIn("IDENTITY_TRAILER_NOT_AUTHORIZED", gate.inspect_commit(record(message="Change\n\nSigned-off-by: malformed")))

    def test_fetch_failure_fails_closed(self):
        event = {"number": 1, "repository": {"full_name": "o/r"}, "pull_request": {"base": {"sha": "a" * 40}, "head": {"sha": "b" * 40}}}
        api = lambda *_: {"head": {"sha": "b" * 40}}
        with self.assertRaisesRegex(gate.GateFailure, "REQUIRED_PR_COMMIT_FETCH_FAILED"):
            gate.verify(event, runner=lambda *_: (_ for _ in ()).throw(gate.GateFailure("REQUIRED_PR_COMMIT_FETCH_FAILED")), api=api)

    def test_head_change_fails_closed(self):
        event = {"number": 1, "repository": {"full_name": "o/r"}, "pull_request": {"base": {"sha": "a" * 40}, "head": {"sha": "b" * 40}}}
        with self.assertRaisesRegex(gate.GateFailure, "PR_HEAD_CHANGED_DURING_INSPECTION"):
            gate.verify(event, api=lambda *_: {"head": {"sha": "c" * 40}})


if __name__ == "__main__":
    unittest.main()
