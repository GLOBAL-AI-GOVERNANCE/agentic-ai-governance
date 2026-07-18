#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import hashlib, re, subprocess, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from tools.canonical_json import canonicalize
from tools.crypto import trusted_key_errors, verify_jws
from tools.strict_json import load_strict
from tools.semantic_rules import (
 SUPPORTED_CRITICAL_EXTENSIONS, parse_time, validate_action_authority_semantics,
 validate_agent_inventory_semantics, validate_assessment_semantics,
 validate_bundle_semantics, validate_data_authority_semantics,
 validate_mcp_inventory_semantics, validate_passport_semantics,
 validate_profile_descriptor_semantics, validate_protected_header,
 validate_revocation_semantics, validate_timestamp,
 validate_tool_inventory_semantics, validate_verification_semantics
)

PUBLIC_SAFETY_PATTERNS={
 'private-key material': r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
 'AWS access-key identifier': r'AKIA[0-9A-Z]{16}',
 'AWS signed-request credential': r'(?:X-Amz-Credential|AWSAccessKeyId)=',
 'AWS signed-request signature': r'X-Amz-' r'Signature=',
 'GitHub token-shaped secret': r'gh[pousr]_[A-Za-z0-9]{20,}',
}

def load(path:Path)->Any:
 return load_strict(path, require_object=path.suffix.lower()==".json")

def domain_id(domain:str,label:str,value:Any)->str:
 return "sha256:"+hashlib.sha256(canonicalize({"domain":domain,label:value})).hexdigest()

def registry(root:Path)->Registry:
 resources=[]
 for path in (root/'schemas').glob('*.json'):
  schema=load(path); Draft202012Validator.check_schema(schema); resources.append((schema['$id'],Resource.from_contents(schema)))
 return Registry().with_resources(resources)
def validate_value_schema(root:Path,schema_name:str,value:Any,store:Registry)->list[str]:
 validator=Draft202012Validator(load(root/'schemas'/schema_name),registry=store,format_checker=FormatChecker())
 return [e.message for e in validator.iter_errors(value)]

def validate_schema(root:Path,schema_name:str,path:Path,store:Registry)->list[str]:
 return validate_value_schema(root,schema_name,load(path),store)

def id_errors(kind:str,value:dict[str,Any])->list[str]:
 errors=[]
 if kind=='bundle':
  src={k:v for k,v in value.items() if k!='bundle_id'}
  if value.get('bundle_id')!=domain_id('global-ai-governance.agentic-assessment-bundle.identifier.v1','manifest',src): errors.append('bundle_id mismatch')
 elif kind=='assessment':
  src={k:v for k,v in value.items() if k!='assessment_id'}
  if value.get('assessment_id')!=domain_id('global-ai-governance.agentic-assessment.identifier.v1','assessment',src): errors.append('assessment_id mismatch')
 elif kind=='passport':
  src={k:v for k,v in value.items() if k not in {'passport_id','proof'}}
  if value.get('passport_id')!=domain_id('global-ai-governance.agent-trust-passport.identifier.v1','passport',src): errors.append('passport_id mismatch')
 elif kind=='revocation':
  for i,e in enumerate(value.get('entries',[])):
   src={k:v for k,v in e.items() if k!='revocation_id'}
   if e.get('revocation_id')!=domain_id('global-ai-governance.agent-trust-passport.revocation-entry.identifier.v1','entry',src): errors.append(f'entries[{i}].revocation_id mismatch')
  src={k:v for k,v in value.items() if k not in {'list_id','proof'}}
  if value.get('list_id')!=domain_id('global-ai-governance.agent-trust-passport.revocation-list.identifier.v1','list',src): errors.append('list_id mismatch')
 return errors

SCHEMA_BY_KIND={'bundle':'bundle-manifest.schema.json','passport':'agent-trust-passport.schema.json','assessment':'assessment-result.schema.json','verification':'verification-result.schema.json','revocation':'revocation-list.schema.json','action':'action-authority.schema.json','data-authority':'data-authority-evidence.schema.json','agent-inventory':'agent-inventory.schema.json','mcp-inventory':'mcp-inventory.schema.json','tool-inventory':'tool-inventory.schema.json','profile-descriptor':'control-profile-descriptor.schema.json','trusted-key':'trusted-key.schema.json'}
SEMANTIC_BY_KIND={'bundle':validate_bundle_semantics,'passport':validate_passport_semantics,'assessment':validate_assessment_semantics,'verification':validate_verification_semantics,'revocation':validate_revocation_semantics,'action':validate_action_authority_semantics,'data-authority':validate_data_authority_semantics,'agent-inventory':validate_agent_inventory_semantics,'mcp-inventory':validate_mcp_inventory_semantics,'tool-inventory':validate_tool_inventory_semantics,'profile-descriptor':validate_profile_descriptor_semantics}

def main()->int:
 root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); errors=[]
 required=['README.md','CONFORMANCE.md','LICENSE','LICENSE_POLICY.md','SECURITY.md','CONTRIBUTING.md','GOVERNANCE.md','.gitignore','.github/CODEOWNERS','.github/workflows/ci.yml','CITATION.cff','tests/negative/index.json','tools/strict_json.py','tools/crypto.py','tools/binding_verification.py','tools/reference_policy.py','examples/quickstart/README.md','examples/passports/signed-unrevoked.json','examples/inventories/agent.json','examples/inventories/mcp.json','examples/inventories/tools.json','examples/action-authority/readonly-graph.json','profiles/mcp-governance-profile.json','decisions/DR-001-public-stewardship.md','decisions/DR-002-licensing-boundary.md','decisions/DR-003-assurance-boundary.md','decisions/DR-004-decision-state-model.md','decisions/DR-005-release-sequencing.md']
 for rel in required:
  if not (root/rel).exists(): errors.append(f'missing {rel}')
 for p in root.rglob('*'):
  if not p.is_file() or any(x in p.parts for x in {'.git','__pycache__','.pytest_cache'}): continue
  if p.suffix.lower() in {'.md','.py','.yml','.yaml','.json','.toml','.cff'}:
   text=p.read_text(encoding='utf-8',errors='replace')
   for label,pattern in PUBLIC_SAFETY_PATTERNS.items():
    if re.search(pattern,text,re.I): errors.append(f'{label} detected in {p.relative_to(root)}')
 if (root/'vv').exists(): errors.append('internal vv directory must not be public')
 requirements=(root/'requirements-dev.txt').read_text(encoding='utf-8').splitlines()
 reqs={line.strip() for line in requirements if line.strip() and not line.startswith('#')}
 if 'pytest==9.0.3' not in reqs: errors.append('pytest must be pinned to patched version 9.0.3')
 if any(line.lower().startswith('pyyaml') for line in reqs): errors.append('unused PyYAML dependency must not be present')
 ci=(root/'.github/workflows/ci.yml').read_text(encoding='utf-8')
 for action in re.findall(r'uses:\s*([^\s#]+)',ci):
  if '@' not in action or not re.fullmatch(r'[0-9a-f]{40}',action.split('@',1)[1]): errors.append(f'GitHub Action is not pinned to a full SHA: {action}')
 if 'persist-credentials: false' not in ci: errors.append('checkout must set persist-credentials: false')
 if 'timeout-minutes:' not in ci: errors.append('CI job must set timeout-minutes')
 codeowners=(root/'.github/CODEOWNERS').read_text(encoding='utf-8')
 if '@GLOBAL-AI-GOVERNANCE/maintainers' in codeowners: errors.append('CODEOWNERS must not reference a nonexistent organization team')
 if '@GLOBAL-AI-GOVERNANCE' not in codeowners: errors.append('CODEOWNERS must reference the repository-owning account')
 citation=(root/'CITATION.cff').read_text(encoding='utf-8')
 if 'Apache-2.0' not in citation or 'CC-BY-4.0' not in citation or 'file-scoped' not in citation: errors.append('CITATION.cff must disclose the file-scoped mixed-license policy')
 if 'git commit --signoff' not in (root/'CONTRIBUTING.md').read_text(encoding='utf-8'): errors.append('CONTRIBUTING.md must explain contribution sign-off')
 schema_prefix='https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance/v0.1.0-alpha.1/schemas/'
 for schema_path in (root/'schemas').glob('*.json'):
  try: schema_doc=load(schema_path)
  except Exception as exc: errors.append(f'{schema_path.relative_to(root)}: strict JSON: {exc}'); continue
  if schema_doc.get('$id') != schema_prefix+schema_path.name: errors.append(f'{schema_path.relative_to(root)}: non-versioned schema $id')
 try: store=registry(root)
 except Exception as exc: errors.append(f'schema registry: {exc}'); store=Registry()
 valid=[
 ('bundle','examples/bundles/valid-bundle-manifest.json'),
 ('passport','examples/passports/unsigned-valid.json'),
 ('passport','examples/passports/signed-revoked.json'),
 ('passport','examples/passports/signed-unrevoked.json'),
 ('trusted-key','examples/trusted-keys/test-ed25519-key.json'),
 ('revocation','examples/revocation/valid-revocation-list.json'),
 ('verification','examples/verification/unsigned-valid-result.json'),
 ('verification','examples/verification/signed-valid-result.json'),
 ('assessment','examples/assessments/approved-readonly.json'),
 ('action','examples/action-authority/readonly-graph.json'),
 ('data-authority','examples/data-authority/synthetic-evidence.json'),
 ('agent-inventory','examples/inventories/agent.json'),
 ('mcp-inventory','examples/inventories/mcp.json'),
 ('tool-inventory','examples/inventories/tools.json'),
 ('profile-descriptor','profiles/mcp-governance-profile.json'),
 ]
 for kind,rel in valid:
  value=load(root/rel)
  for e in validate_schema(root,SCHEMA_BY_KIND[kind],root/rel,store): errors.append(f'{rel}: schema: {e}')
  if kind in SEMANTIC_BY_KIND:
   for e in SEMANTIC_BY_KIND[kind](value): errors.append(f'{rel}: semantic: {e}')
  for e in id_errors(kind,value): errors.append(f'{rel}: identifier: {e}')
 key=load(root/'examples/trusted-keys/test-ed25519-key.json')
 for rel,typ,cty in [('examples/passports/signed-revoked.json','atp+jws','application/agent-trust-passport+json'),('examples/revocation/valid-revocation-list.json','atp-revocation+jws','application/agent-revocation-list+json')]:
  for e in verify_jws(load(root/rel),key,typ=typ,cty=cty): errors.append(f'{rel}: crypto: {e}')
 vector={'€':'Euro Sign','\r':'Carriage Return','דּ':'Hebrew Letter Dalet With Dagesh','1':'One','😀':'Emoji: Grinning Face','\u0080':'Control','ö':'Latin Small Letter O With Diaeresis'}
 expected='{"\\r":"Carriage Return","1":"One","\u0080":"Control","ö":"Latin Small Letter O With Diaeresis","€":"Euro Sign","😀":"Emoji: Grinning Face","דּ":"Hebrew Letter Dalet With Dagesh"}'.encode()
 if canonicalize(vector)!=expected: errors.append('RFC 8785 UTF-16 property-order vector mismatch')
 index=load(root/'tests/negative/index.json'); listed=[c['file'] for c in index['cases']]
 actual=sorted(p.name for p in (root/'tests/negative').glob('*.json') if p.name!='index.json')
 if sorted(listed)!=actual: errors.append(f'negative index mismatch: listed={len(listed)} actual={len(actual)}')
 for case in index['cases']:
  rel='tests/negative/'+case['file']; value=load(root/rel); rejected=[]; validator=case['validator']; kind=case['kind']
  if validator=='artifact':
   schema_kind='passport' if kind=='timestamp-passport' else kind
   rejected+=validate_schema(root,SCHEMA_BY_KIND[schema_kind],root/rel,store)
   fn=SEMANTIC_BY_KIND.get(schema_kind)
   if fn: rejected+=fn(value)
  elif validator=='semantic': rejected+=SEMANTIC_BY_KIND[kind](value)
  elif validator=='identifier': rejected+=id_errors(kind,value)
  elif validator=='protected_header':
   rejected+=validate_protected_header(value,content_type='application/agent-trust-passport+json',type_value='atp+jws')
   if value.get('kid')!=key.get('kid'): rejected.append('protected header kid does not match trusted key')
  elif validator=='critical_extensions':
   rejected += [f'unsupported critical extension: {name}' for name in sorted(set(value.get('critical_extensions',[]))-SUPPORTED_CRITICAL_EXTENSIONS)]
  elif validator=='version':
   if value.get('schema_version')!='0.1.0-alpha.1': rejected.append('unsupported schema version')
  elif validator=='trusted_key':
   rejected += trusted_key_errors(value,expected_issuer=None,at_time=parse_time('2026-07-18T12:00:00Z'))
  if not rejected: errors.append(f'negative accepted: {rel}')
 from tools.strict_json import StrictJSONError
 for rel in ['malformed.json','duplicate-key.json','nonfinite.json','unsafe-integer.json','top-level-list.json','invalid-utf8.bin']:
  try: load_strict(root/'tests/cli-negative'/rel,require_object=True)
  except StrictJSONError: pass
  else: errors.append(f'strict JSON fixture accepted: tests/cli-negative/{rel}')
 cli=subprocess.run([sys.executable,str(root/'tools/validate_artifact.py'),'--kind','passport','--trusted-key',str(root/'examples/trusted-keys/test-ed25519-key.json'),'--revocation-list',str(root/'examples/revocation/valid-revocation-list.json'),'--bundle-manifest',str(root/'examples/bundles/valid-bundle-manifest.json'),'--bundle-root',str(root),'--at-time','2026-07-18T12:00:00Z',str(root/'examples/passports/signed-unrevoked.json')],capture_output=True,text=True)
 if cli.returncode: errors.append('end-user signed-passport validation did not produce VALID')
 else:
  try:
   report=__import__('json').loads(cli.stdout)
   if (not report.get('fully_validated') or report.get('issued_assessment_result')!='APPROVED' or report.get('verification_primary_status')!='VALID' or report.get('operating_disposition')!='PERMITTED' or 'decision' in report): errors.append('end-user validator did not preserve the three-layer APPROVED / VALID / PERMITTED result')
  except Exception as exc: errors.append(f'end-user validator output is not JSON: {exc}')
 r=subprocess.run([sys.executable,str(root/'tools/build_dist.py'),'--check',str(root)],capture_output=True,text=True)
 if r.returncode: errors.append(r.stdout.strip() or r.stderr.strip())
 if errors:
  print('CONFORMANCE FAILED'); [print('-',e) for e in errors]; return 1
 print('CONFORMANCE PASSED'); print('schemas:',len(list((root/'schemas').glob('*.json')))); print('negative fixtures:',len(index['cases'])); print('repository invariants: clean'); return 0
if __name__=='__main__': raise SystemExit(main())
