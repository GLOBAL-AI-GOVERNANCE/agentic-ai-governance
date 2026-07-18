# SPDX-License-Identifier: Apache-2.0
from copy import deepcopy
from pathlib import Path
from tools.verify_repository import verify_jws
from tools.strict_json import load_strict

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    return load_strict(ROOT / rel, require_object=True)

def test_passport_signature_and_header():
    document=load('examples/passports/signed-revoked.json'); key=load('examples/trusted-keys/test-ed25519-key.json')
    assert not verify_jws(document,key,typ='atp+jws',cty='application/agent-trust-passport+json')

def test_revocation_signature_and_header():
    document=load('examples/revocation/valid-revocation-list.json'); key=load('examples/trusted-keys/test-ed25519-key.json')
    assert not verify_jws(document,key,typ='atp-revocation+jws',cty='application/agent-revocation-list+json')

def test_altered_signature_rejected():
    document=load('examples/passports/signed-revoked.json'); key=load('examples/trusted-keys/test-ed25519-key.json')
    changed=deepcopy(document); jws=changed['proof']['jws']; changed['proof']['jws']=jws[:-1]+('A' if jws[-1] != 'A' else 'B')
    assert verify_jws(changed,key,typ='atp+jws',cty='application/agent-trust-passport+json')

def test_wrong_kid_rejected():
    document=load('examples/passports/signed-revoked.json'); key=deepcopy(load('examples/trusted-keys/test-ed25519-key.json')); key['kid']='wrong'
    assert verify_jws(document,key,typ='atp+jws',cty='application/agent-trust-passport+json')

def test_malformed_base64url_rejected():
    document=deepcopy(load('examples/passports/signed-revoked.json')); key=load('examples/trusted-keys/test-ed25519-key.json')
    a,b,c=document['proof']['jws'].split('.'); document['proof']['jws']='!'+a+'..'+c
    assert verify_jws(document,key,typ='atp+jws',cty='application/agent-trust-passport+json')


def test_noncanonical_base64url_rejected():
    document=deepcopy(load('examples/revocation/valid-revocation-list.json')); key=load('examples/trusted-keys/test-ed25519-key.json')
    a,b,c=document['proof']['jws'].split('.')
    # Change only unused trailing base64url bits. Decoded bytes may match unless canonical encoding is enforced.
    c2=c[:-1]+('B' if c[-1] != 'B' else 'C')
    document['proof']['jws']=a+'..'+c2
    assert verify_jws(document,key,typ='atp-revocation+jws',cty='application/agent-revocation-list+json')
