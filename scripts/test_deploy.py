"""Verify deployment success and rollback control flow without a live server."""
import os, shutil, subprocess, tempfile, unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().with_name('deploy.sh')
OLD='sha-'+'1'*40
NEW='sha-'+'2'*40
class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='venuevista-deploy-test-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.bin=self.root/'bin';self.bin.mkdir()
        shutil.copy(SCRIPT,self.root/'deploy.sh')
        (self.root/'.env').write_text('DB_PASSWORD=example\nORACLE_PASSWORD=example\nUI_PORT=4200\n')
        (self.root/'compose.deploy.yaml').write_text('services: {}\n')
        (self.root/'current.env').write_text('IMAGE_REPOSITORY=owner/repository\nIMAGE_TAG='+OLD+'\n')
        fake=self.bin/'docker'
        fake.write_text('''#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$TEST_ROOT/docker.log"
if [[ "$*" == *" pull backend frontend"* && "${FAIL_PULL:-0}" == 1 ]]; then exit 1; fi
if [[ "$*" == *" up -d --wait --wait-timeout 900"* && "${FAIL_UP:-0}" == 1 ]]; then exit 1; fi
exit 0
''');fake.chmod(0o755)
        (self.root/'check_health.sh').write_text('#!/usr/bin/env bash\nexit "${FAIL_HEALTH:-0}"\n')
        self.env={**os.environ,'PATH':str(self.bin)+os.pathsep+os.environ['PATH'],'TEST_ROOT':str(self.root)}
    def run_release(self,tag=NEW,**env):
        return subprocess.run(['bash','deploy.sh','owner/repository',tag],cwd=self.root,env={**self.env,**env},text=True,capture_output=True)
    def test_success_records_new_release_and_retains_previous(self):
        r=self.run_release();self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(NEW,(self.root/'current.env').read_text());self.assertIn(OLD,(self.root/'previous.env').read_text())
    def test_health_failure_restores_previous_pair_and_fails(self):
        r=self.run_release(FAIL_HEALTH='1');self.assertNotEqual(r.returncode,0)
        self.assertIn('--env-file previous.env',(self.root/'docker.log').read_text());self.assertIn(OLD,(self.root/'current.env').read_text())
    def test_startup_failure_restores_previous_pair_and_fails(self):
        r=self.run_release(FAIL_UP='1');self.assertNotEqual(r.returncode,0)
        self.assertIn('--env-file previous.env',(self.root/'docker.log').read_text());self.assertIn(OLD,(self.root/'current.env').read_text())
    def test_pull_failure_leaves_current_release_untouched(self):
        r=self.run_release(FAIL_PULL='1');self.assertNotEqual(r.returncode,0)
        self.assertIn(OLD,(self.root/'current.env').read_text());self.assertNotIn(' up -d ',(self.root/'docker.log').read_text())
    def test_invalid_tag_never_invokes_docker(self):
        r=self.run_release(tag='latest');self.assertNotEqual(r.returncode,0);self.assertFalse((self.root/'docker.log').exists())
if __name__=='__main__':unittest.main(verbosity=2)
